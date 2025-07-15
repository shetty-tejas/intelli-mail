#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { InfraStack } from '../lib/infra-stack';
import { VpcStack } from '../lib/vpc';

const app = new cdk.App();


const vpcStack = new VpcStack(app, 'VpcStack');

new InfraStack(app, 'InfraStack', {
  vpc: vpcStack.vpc,
});