import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';

export class AgentStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    new bedrock.CfnAgent(this, 'MyBedrockAgent', {
      agentName: 'my-bedrock-agent',
      foundationModel: 'anthropic.claude-v2', // Example model
      instruction: 'You are a helpful assistant.',
      // Add other required properties here
    });

  }
}
