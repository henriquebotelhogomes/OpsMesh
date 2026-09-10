param location string = resourceGroup().location
param environmentName string = 'env-opsmesh'
param containerAppName string = 'opsmesh-app'
param containerImage string = 'mcr.microsoft.com/azuredocs/aci-helloworld:latest'

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  properties: {
    zoneRedundant: false
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
      }
    }
    template: {
      containers: [
        {
          name: 'opsmesh'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'APP_ENV'
              value: 'production'
            }
            {
              name: 'DEMO_MODE'
              value: 'true'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0 // FinOps Scale-to-Zero ($0 at rest)
        maxReplicas: 2
      }
    }
  }
}
