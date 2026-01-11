from datetime import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
import inspect

dag_name = "nessie-minio-dag"
app_file = "/mnt/spark/work/app.py"

def application():
    import pyspark
    from pyspark.sql import SparkSession

    if __name__ == "__main__":
        """
            Usage: pi [partitions]
        """
        spark = SparkSession.builder.appName("nessie-minio").getOrCreate()

        ## Create a Table
        #spark.sql("CREATE TABLE nessie.names (name STRING) USING iceberg;").show()
        ## Insert Some Data
        spark.sql("INSERT INTO nessie.names VALUES ('Alex Merced'), ('Dipankar Mazumdar'), ('Jason Hughes')").show()
        ## Query the Data
        spark.sql("SELECT * FROM nessie.names;").show()

        spark.stop()

def print_func(func):
    """Gets the body of function a1 without declaration and indentation."""
    # Get the full source code
    source_code = inspect.getsource(func).replace("'", "'\\''")

    # Split into lines and remove the function declaration
    lines = source_code.split('\n')
    body_lines = lines[1:]  # Skip the first line (declaration)

    # Determine indentation of first line in body
    first_line = body_lines[0] if body_lines else ""
    indent = len(first_line) - len(first_line.lstrip())

    # Remove that indentation from all lines
    clean_lines = [line[indent:] if line.strip() else line for line in body_lines]

    # Join back into a single string
    clean_source = '\n'.join(clean_lines)
    return clean_source

def write_string_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

application_code=print_func(application)

# Define the DAG
dag = DAG(
    dag_name,
    description='Spark Kubernetes DAG for Nessie and MinIO',
    schedule_interval=None,  # Disable automatic scheduling for manual runs
    start_date=datetime(2023, 1, 1),
    catchup=False
)


template_spec = {
    'apiVersion': 'sparkoperator.k8s.io/v1beta2',
    'kind': 'SparkApplication',
    'metadata': {
        'name': 'nessie-minio-dag',
        'namespace': 'spark-operator'
    },
    'spec': {
        'type': 'Python',
        'pythonVersion': '3',
        'mode': 'cluster',
        'image': 'johnwongapi/spark-nessie:3.5.5',
        'imagePullPolicy': 'IfNotPresent',
        'mainApplicationFile': f'local://{app_file}',
        'sparkVersion': '3.5.5',
        'volumes': [
            {
                'name': 'spark-work',
                'emptyDir': {}
            }
        ],
        'dynamicAllocation': {
            'enabled': True,
            'initialExecutors': 2,
            'minExecutors': 2,
            'maxExecutors': 4
        },
        'deps': {
            'jars': [
                'local:///opt/spark/jars-extra/iceberg-spark-runtime-3.5_2.12-1.9.0.jar',
                'local:///opt/spark/jars-extra/nessie-spark-extensions-3.5_2.12-0.103.6.jar',
                'local:///opt/spark/jars-extra/bundle-2.31.0.jar',
                'local:///opt/spark/jars-extra/url-connection-client-2.31.0.jar'
            ]
        },
        'sparkConf': {
            'spark.app.name': 'nessie-minio-dag',
            # "spark.jars.packages": "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.9.0,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.103.6,software.amazon.awssdk:bundle:2.31.0,software.amazon.awssdk:url-connection-client:2.31.0",
            'spark.kubernetes.file.upload.path': '/mnt/spark/work',
            'spark.sql.extensions': 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions',
            'spark.sql.catalog.nessie': 'org.apache.iceberg.spark.SparkCatalog',
            'spark.sql.catalog.nessie.uri': 'http://nessie.nessie-ns:19120/api/v1',
            'spark.sql.catalog.nessie.ref': 'main',
            'spark.sql.catalog.nessie.authentication.type': 'NONE',
            'spark.sql.catalog.nessie.catalog-impl': 'org.apache.iceberg.nessie.NessieCatalog',
            'spark.sql.catalog.nessie.s3.endpoint': 'http://minio.minio:9000',
            'spark.sql.catalog.nessie.warehouse': 's3a://nessiedemo01/folder1',
            'spark.sql.catalog.nessie.io-impl': 'org.apache.iceberg.aws.s3.S3FileIO',
            'spark.sql.catalog.nessie.s3.path-style-access': 'true',
            'spark.sql.catalog.nessie.s3.region': 'us-east-1',
            'spark.sql.catalog.nessie.s3.access-key-id': 'minioadmin',
            'spark.sql.catalog.nessie.s3.secret-access-key': 'minioadmin',
            # "spark.jars.ivy": "/tmp/ivy"
        },
        'driver': {
            'labels': {
                'version': '3.5.5'
            },
            'cores': 1,
            'memory': '512m',
            'initContainers': [
                {
                    'command': ['sh', '-c'],
                    'args': [
                        f"echo '{application_code}' > {app_file}"
                    ],
                    'image': 'johnwongapi/spark-nessie:3.5.5',
                    'name': 'import-app',
                    'volumeMounts': [
                        {
                            'name': 'spark-work',
                            'mountPath': '/mnt/spark/work'
                        }
                    ]
                }
            ],
            'volumeMounts': [
                {
                    'name': 'spark-work',
                    'mountPath': '/mnt/spark/work'
                }
            ],
            'serviceAccount': 'spark-operator-spark',
            'env': [
                {
                    'name': 'AWS_REGION',
                    'value': 'us-east-1'
                }
            ]
        },
        'executor': {
            'labels': {
                'version': '3.5.5'
            },
            'instances': 1,
            'cores': 1,
            'memory': '512m',
            'env': [
                {
                    'name': 'AWS_REGION',
                    'value': 'us-east-1'
                }
            ]
        }
    }
}


spark_kubernetes_job = SparkKubernetesOperator(
    task_id=dag_name,
    namespace='spark-operator',  # Kubernetes namespace
    template_spec=template_spec,  # Path to your spark application YAML file
    kubernetes_conn_id='test0',  # Connection ID for Kubernetes
    do_xcom_push=False,
    dag=dag
)

spark_kubernetes_job
