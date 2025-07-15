import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import path from 'path';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from "aws-cdk-lib/aws-elasticloadbalancingv2";

export interface InfraStackProps extends cdk.StackProps {
  readonly vpc: ec2.Vpc;
}

export class InfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: InfraStackProps) {
    super(scope, id, props);

    const ecsLogGroup = new logs.LogGroup(this, 'ECSLogGroup', {
        logGroupName: '/ecs/mcp-on-ecs',
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        retention: logs.RetentionDays.ONE_DAY,
    });

    const asset = new ecrAssets.DockerImageAsset(this, 'ImageAsset', {
      directory: path.join(__dirname, '../../'),
      exclude: ['cdk.out', 'infra/cdk.out', '.git', 'node_modules', 'infra/node_modules'],
    });

    const image = ecs.ContainerImage.fromDockerImageAsset(asset);

    
    const cluster = new ecs.Cluster(this, 'Cluster', {
      clusterName: 'mcp-on-ecs-cluster',
      vpc: props.vpc,
    });

    const policy = new iam.PolicyStatement({
      actions: ['ecr:*'],
      resources: ['*'],
    });

    const taskRole = new iam.Role(this, 'TaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchFullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy'),
      ],
      inlinePolicies: {
        ecr: new iam.PolicyDocument({
          statements: [policy],
        }),
      },
    });

    const taskDef = new ecs.FargateTaskDefinition(this, 'Task', {
      memoryLimitMiB: 1024,
      cpu: 512,
      taskRole,
      executionRole: taskRole,
      runtimePlatform: {
        operatingSystemFamily: ecs.OperatingSystemFamily.LINUX,
        cpuArchitecture: ecs.CpuArchitecture.ARM64,
      },
    });

    taskDef.addContainer('AppContainer', {
      image: image,
      logging: ecs.LogDriver.awsLogs({
        streamPrefix: 'mcp-on-ecs',
        logGroup: ecsLogGroup,
      }),
      portMappings: [
        {
          containerPort: 8000,
          hostPort: 8000,
        },
      ],
     }
    );

    const loadBalancedFargateService = new ecsPatterns.ApplicationLoadBalancedFargateService(this, 'Service', {
      cluster,
      desiredCount: 1,
      taskDefinition: taskDef,
      publicLoadBalancer: true,
      circuitBreaker: {
        rollback: true,
      },
      listenerPort: 8000,
      protocol: elbv2.ApplicationProtocol.HTTP,
    });

    loadBalancedFargateService.targetGroup.configureHealthCheck({
      path: '/sse',
      port: '8000',
      interval: cdk.Duration.seconds(30),
      timeout: cdk.Duration.seconds(5),
      healthyThresholdCount: 2,
      unhealthyThresholdCount: 2,
      healthyHttpCodes: '307',
    });

    new cdk.CfnOutput(this, 'LoadBalancerDNS', {
      value: loadBalancedFargateService.loadBalancer.loadBalancerDnsName,
    });

    new cdk.CfnOutput(this, 'ImageURI', {
      value: asset.imageUri,
    });

  }
}