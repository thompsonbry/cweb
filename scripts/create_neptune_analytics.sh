#!/bin/bash
# Script to create a Neptune Analytics graph using AWS CLI

# Default values
GRAPH_NAME="cweb-graph"
REGION="us-east-1"
INSTANCE_TYPE="db.r6g.4xlarge"  # 16GB RAM
VECTOR_DIMENSIONS=1024

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --name)
      GRAPH_NAME="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --instance-type)
      INSTANCE_TYPE="$2"
      shift 2
      ;;
    --vector-dimensions)
      VECTOR_DIMENSIONS="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Creating Neptune Analytics graph: $GRAPH_NAME"
echo "Region: $REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo "Vector Dimensions: $VECTOR_DIMENSIONS"

# Configure vector search
VECTOR_CONFIG="{\"vectorSearchConfiguration\":{\"dimension\":$VECTOR_DIMENSIONS,\"similarityMetric\":\"cosine\"}}"

# Create the graph
RESPONSE=$(aws neptune-graph create-graph \
  --graph-name "$GRAPH_NAME" \
  --instance-type "$INSTANCE_TYPE" \
  --graph-options "$VECTOR_CONFIG" \
  --tags Key=Project,Value=CWEB Key=Environment,Value=Development \
  --region "$REGION" \
  --output json)

# Extract the graph ID
GRAPH_ID=$(echo $RESPONSE | jq -r '.id')

if [ -z "$GRAPH_ID" ]; then
  echo "Failed to create graph"
  exit 1
fi

echo "Graph creation initiated. Graph ID: $GRAPH_ID"
echo "Waiting for graph to become available..."

# Wait for the graph to become available
aws neptune-graph wait graph-available \
  --id "$GRAPH_ID" \
  --region "$REGION"

# Get the graph details
GRAPH_DETAILS=$(aws neptune-graph get-graph \
  --id "$GRAPH_ID" \
  --region "$REGION" \
  --output json)

# Extract the endpoint
ENDPOINT=$(echo $GRAPH_DETAILS | jq -r '.endpoint')

echo "Graph is now available!"
echo "Endpoint: $ENDPOINT"
echo ""
echo "Add the following to your .env file:"
echo "NEPTUNE_ENDPOINT=$ENDPOINT"
echo "NEPTUNE_PORT=8182"
echo "NEPTUNE_AUTH_MODE=IAM"
echo "NEPTUNE_REGION=$REGION"
