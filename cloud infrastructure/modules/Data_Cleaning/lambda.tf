resource "local_file" "requirements" {
  content  = "pymupdf"
  filename = "${path.module}/requirements.txt"
}

resource "null_resource" "build_lambda_layer" {
  triggers = {
    # Re-build if the requirements change
    requirements_hash = md5("pymupdf")
  }

  provisioner "local-exec" {
    # This command downloads Linux binaries directly to your Mac
    command = <<EOT
      mkdir -p ${path.module}/layer_content/python
      pip install \
        --platform manylinux2014_x86_64 \
        --target ${path.module}/layer_content/python \
        --implementation cp \
        --python-version 3.8 \
        --only-binary=:all: \
        --upgrade \
        pymupdf
    EOT
  }
}

resource "aws_lambda_layer_version" "package_layer" {
  filename            = data.archive_file.layer_zip.output_path
  source_code_hash    = data.archive_file.layer_zip.output_base64sha256
  layer_name          = "pymupdf_lib"
  compatible_runtimes = ["python3.8"]
}

data "archive_file" "lambda_file" {
  type = "zip"
  source_file = "${path.module}/lambda_function.py"
  output_path = "${path.module}/lamdba_function_payload.zip"
}
