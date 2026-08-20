@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Environment name used in resource names.')
@allowed([
  'dev'
  'test'
  'prod'
])
param environment string = 'dev'

@description('Short project name used in resource names.')
param projectName string = 'saaspipeline'

@secure()
@description('Synapse SQL administrator password. Use a secret value in real deployments.')
param synapseSqlAdminPassword string = 'ReplaceWithSecurePassword123!'

var suffix = uniqueString(resourceGroup().id, projectName, environment)
var storageName = toLower('${projectName}${environment}${suffix}')
var dataFactoryName = '${projectName}-${environment}-adf-${suffix}'
var synapseName = '${projectName}-${environment}-syn-${suffix}'
var keyVaultName = '${projectName}-${environment}-kv-${suffix}'
var logAnalyticsName = '${projectName}-${environment}-log-${suffix}'

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

resource rawContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/raw'
  properties: {
    publicAccess: 'None'
  }
}

resource curatedContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/curated'
  properties: {
    publicAccess: 'None'
  }
}

resource quarantineContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/quarantine'
  properties: {
    publicAccess: 'None'
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enabledForTemplateDeployment: true
  }
}

resource dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: dataFactoryName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
}

resource synapse 'Microsoft.Synapse/workspaces@2021-06-01' = {
  name: synapseName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    defaultDataLakeStorage: {
      accountUrl: storage.properties.primaryEndpoints.dfs
      filesystem: 'curated'
    }
    managedResourceGroupName: '${synapseName}-managed-rg'
    sqlAdministratorLogin: 'synadmin'
    sqlAdministratorLoginPassword: synapseSqlAdminPassword
  }
  dependsOn: [
    curatedContainer
  ]
}

resource dataFactoryDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'send-adf-logs-to-log-analytics'
  scope: dataFactory
  properties: {
    workspaceId: logAnalytics.id
    logs: [
      {
        category: 'PipelineRuns'
        enabled: true
      }
      {
        category: 'ActivityRuns'
        enabled: true
      }
      {
        category: 'TriggerRuns'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

output storageAccountName string = storage.name
output dataFactoryName string = dataFactory.name
output synapseWorkspaceName string = synapse.name
output keyVaultName string = keyVault.name
output logAnalyticsWorkspaceName string = logAnalytics.name
