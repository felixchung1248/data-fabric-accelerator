FROM apache/spark:3.5.5

USER root

# Set environment variables
ENV SPARK_HOME=/opt/spark
ENV IVY_CACHE_DIR=/opt/spark/ivy-cache

# Create directories for JARs
RUN mkdir -p $SPARK_HOME/jars-extra $IVY_CACHE_DIR

# Download required JARs
RUN wget -P $SPARK_HOME/jars-extra/ \
    https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.9.0/iceberg-spark-runtime-3.5_2.12-1.9.0.jar \
    https://repo1.maven.org/maven2/org/projectnessie/nessie-integrations/nessie-spark-extensions-3.5_2.12/0.103.6/nessie-spark-extensions-3.5_2.12-0.103.6.jar \
    https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.31.0/bundle-2.31.0.jar \
    https://repo1.maven.org/maven2/software/amazon/awssdk/url-connection-client/2.31.0/url-connection-client-2.31.0.jar

# Set permissions
RUN chmod 644 $SPARK_HOME/jars-extra/*.jar
RUN chown -R spark:spark $SPARK_HOME/jars-extra $IVY_CACHE_DIR

USER spark
