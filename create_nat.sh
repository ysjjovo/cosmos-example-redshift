#!/bin/bash

# 设置变量
VPC_ID="your-vpc-id"  # 替换为你的 VPC ID
SUBNET_ID="subnet-06d9788819596ff46"  # 替换为你的公有子网 ID
ROUTE_TABLE_ID="rtb-0b4858d28c9e367b9"  # 替换为你的路由表 ID
NAT_GATEWAY_NAME="lin"  # 替换为你的 NAT 网关名称

ALLOCATION_ID=$(aws ec2 allocate-address --output text --query 'AllocationId')
# 创建 NAT 网关
echo "Creating NAT gateway..."
NAT_GATEWAY_ID=$(aws ec2 create-nat-gateway --subnet-id $SUBNET_ID --allocation-id=$ALLOCATION_ID --output text --query 'NatGateway.NatGatewayId')
if [ -z "$NAT_GATEWAY_ID" ]; then
  echo "Failed to create NAT gateway"
  exit 1
fi
echo "NAT gateway created with ID: $NAT_GATEWAY_ID"

# 等待 NAT 网关可用
echo "Waiting for NAT gateway to become available..."
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GATEWAY_ID
echo "NAT gateway is available"

# 将 NAT 网关与路由表关联
echo "Associating NAT gateway with route table..."
aws ec2 associate-route-table --route-table-id $ROUTE_TABLE_ID --nat-gateway-id $NAT_GATEWAY_ID
if [ $? -ne 0 ]; then
  echo "Failed to associate NAT gateway with route table"
  exit 1
fi
echo "NAT gateway associated with route table successfully"