resource "pinecone_index" "serverless" {
  name      = var.pinecone
  dimension = 1536
  spec = {
    serverless = {
      cloud  = var.cloud
      region = var.pinecone_region
    }
  }
}
