from django.db import migrations


CERTIFICATIONS = [
    # ── Must Have ──────────────────────────────────────────────────────────────
    {
        "titulo": "dbt Certified Developer",
        "fornecedor": "dbt Labs",
        "categoria": "Analytics Engineering / Modern Data Stack",
        "nivel": "Mid-level",
        "prioridade": "must_have",
        "descricao": (
            "The official dbt certification covering data transformation, ELT modelling, "
            "testing, documentation, and modern analytics engineering workflows. "
            "Near-mandatory for any AE working with dbt Core or dbt Cloud."
        ),
        "tags": "dbt,ELT,data modeling,analytics engineering,transformation",
        "link_oficial": "https://www.getdbt.com/certifications/analytics-engineer-certification-exam",
        "link_curso": "https://learn.getdbt.com/courses/dbt-fundamentals",
    },
    {
        "titulo": "Microsoft PL-300 — Power BI Data Analyst Associate",
        "fornecedor": "Microsoft",
        "categoria": "BI & Visualization",
        "nivel": "Mid-level",
        "prioridade": "must_have",
        "descricao": (
            "Validates ability to design and build scalable data models, clean and transform "
            "data, and enable advanced analytics in Power BI. Covers DAX, data modelling, "
            "storytelling and performance optimisation. Highly valued in enterprise environments."
        ),
        "tags": "Power BI,DAX,data modeling,BI,storytelling,visualization",
        "link_oficial": "https://learn.microsoft.com/en-us/credentials/certifications/power-bi-data-analyst-associate/",
        "link_curso": "https://learn.microsoft.com/en-us/training/paths/get-started-power-bi/",
    },
    {
        "titulo": "DP-600 — Microsoft Fabric Analytics Engineer Associate",
        "fornecedor": "Microsoft",
        "categoria": "Analytics Engineering / Modern Data Stack",
        "nivel": "Mid-level",
        "prioridade": "must_have",
        "descricao": (
            "One of the most aligned certifications to the Analytics Engineer role today. "
            "Covers Lakehouse architecture, semantic models, governance, data pipelines, "
            "and the full Microsoft Fabric + Power BI ecosystem. Essential for teams on the Microsoft stack."
        ),
        "tags": "Microsoft Fabric,Lakehouse,semantic model,governance,Power BI,pipelines",
        "link_oficial": "https://learn.microsoft.com/en-us/credentials/certifications/fabric-analytics-engineer-associate/",
        "link_curso": "https://learn.microsoft.com/en-us/training/paths/get-started-fabric/",
    },
    {
        "titulo": "SnowPro Core Certification",
        "fornecedor": "Snowflake",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Mid-level",
        "prioridade": "must_have",
        "descricao": (
            "Validates expertise in Snowflake's cloud data platform: warehouse architecture, "
            "performance tuning, security, virtual warehouses, and advanced SQL. "
            "Highly sought after in companies running a modern data stack."
        ),
        "tags": "Snowflake,cloud,data warehouse,SQL,performance,security",
        "link_oficial": "https://learn.snowflake.com/en/certifications/snowpro-core/",
        "link_curso": "",
    },
    {
        "titulo": "Databricks Certified Data Engineer Associate",
        "fornecedor": "Databricks",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Mid-level",
        "prioridade": "must_have",
        "descricao": (
            "Covers Apache Spark, Delta Lake, Medallion Architecture and data pipeline design "
            "on the Databricks Lakehouse platform. One of the strongest certifications for "
            "modern pipeline engineering and large-scale data processing."
        ),
        "tags": "Databricks,Spark,Delta Lake,Medallion Architecture,pipelines,lakehouse",
        "link_oficial": "https://www.databricks.com/learn/certification/data-engineer-associate",
        "link_curso": "",
    },
    # ── Recommended – Cloud ────────────────────────────────────────────────────
    {
        "titulo": "AWS Certified Data Engineer — Associate",
        "fornecedor": "Amazon Web Services",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Mid-level",
        "prioridade": "recommended",
        "descricao": (
            "Covers core AWS data services including Glue, Redshift, Kinesis, Lake Formation "
            "and ETL best practices. Highly requested in enterprise environments that run "
            "data workloads on AWS."
        ),
        "tags": "AWS,Glue,Redshift,Kinesis,Lake Formation,ETL,cloud",
        "link_oficial": "https://aws.amazon.com/certification/certified-data-engineer-associate/",
        "link_curso": "",
    },
    {
        "titulo": "Google Cloud Professional Data Engineer",
        "fornecedor": "Google Cloud",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Senior",
        "prioridade": "recommended",
        "descricao": (
            "One of the most technically respected cloud certifications. Covers BigQuery, "
            "Dataflow, Pub/Sub, ML pipelines and GCP data ecosystem design. "
            "Strong signal of end-to-end data engineering maturity."
        ),
        "tags": "Google Cloud,BigQuery,Dataflow,Pub/Sub,ML pipelines,GCP",
        "link_oficial": "https://cloud.google.com/learn/certification/data-engineer",
        "link_curso": "",
    },
    {
        "titulo": "DP-700 — Microsoft Fabric Data Engineer Associate",
        "fornecedor": "Microsoft",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Senior",
        "prioridade": "recommended",
        "descricao": (
            "The data engineering counterpart to DP-600, focused on building and maintaining "
            "data pipelines within Microsoft Fabric. Gradually replacing the older Azure Data "
            "Engineer (DP-203) as Fabric becomes the primary Microsoft data platform."
        ),
        "tags": "Microsoft Fabric,data pipelines,Azure,data engineering,lakehouse",
        "link_oficial": "https://learn.microsoft.com/en-us/credentials/certifications/fabric-data-engineer-associate/",
        "link_curso": "",
    },
    # ── Recommended – BI / Analytics ──────────────────────────────────────────
    {
        "titulo": "Tableau Certified Data Analyst",
        "fornecedor": "Tableau (Salesforce)",
        "categoria": "BI & Visualization",
        "nivel": "Mid-level",
        "prioridade": "recommended",
        "descricao": (
            "Validates the ability to connect to data, perform analysis, and build compelling "
            "dashboards in Tableau. Good for analytics roles with a strong focus on "
            "data visualisation and storytelling."
        ),
        "tags": "Tableau,visualization,analytics,storytelling,dashboards",
        "link_oficial": "https://www.tableau.com/learn/certification/certified-data-analyst",
        "link_curso": "",
    },
    {
        "titulo": "Looker Business Intelligence Analyst",
        "fornecedor": "Google / Looker",
        "categoria": "BI & Visualization",
        "nivel": "Mid-level",
        "prioridade": "recommended",
        "descricao": (
            "Covers LookML, Looker dashboards and Google Cloud BI workflows. "
            "Very useful for teams on the Google Cloud stack or using Looker as the "
            "primary BI tool."
        ),
        "tags": "Looker,LookML,Google Cloud,BI,dashboards",
        "link_oficial": "https://cloud.google.com/looker/docs/looker-certifications",
        "link_curso": "",
    },
    # ── Complementary ─────────────────────────────────────────────────────────
    {
        "titulo": "Astronomer Certification for Apache Airflow",
        "fornecedor": "Astronomer",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Mid-level",
        "prioridade": "complementary",
        "descricao": (
            "Validates knowledge of Apache Airflow for orchestrating data pipelines. "
            "Covers DAGs, operators, scheduling, sensors and Astronomer-specific features. "
            "Very relevant for AEs managing complex pipeline dependencies."
        ),
        "tags": "Airflow,orchestration,DAGs,pipelines,scheduling",
        "link_oficial": "https://www.astronomer.io/certification/",
        "link_curso": "",
    },
    {
        "titulo": "Confluent Certified Developer for Apache Kafka",
        "fornecedor": "Confluent",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Senior",
        "prioridade": "complementary",
        "descricao": (
            "Covers Kafka architecture, producers/consumers, streaming, Schema Registry "
            "and event-driven data pipelines. Excellent differentiator for AEs working "
            "with real-time or near-real-time data."
        ),
        "tags": "Kafka,streaming,real-time,event-driven,pipelines,Confluent",
        "link_oficial": "https://developer.confluent.io/certification/",
        "link_curso": "",
    },
    {
        "titulo": "HashiCorp Terraform Associate",
        "fornecedor": "HashiCorp",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Mid-level",
        "prioridade": "complementary",
        "descricao": (
            "Covers Infrastructure as Code concepts with Terraform: state management, "
            "modules, providers and workspaces. A strong differentiator for senior AEs "
            "who manage cloud data infrastructure."
        ),
        "tags": "Terraform,IaC,infrastructure,cloud,DevOps",
        "link_oficial": "https://www.hashicorp.com/certification/terraform-associate",
        "link_curso": "",
    },
    {
        "titulo": "Databricks Certified Data Engineer Professional",
        "fornecedor": "Databricks",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Senior",
        "prioridade": "complementary",
        "descricao": (
            "Advanced-level certification covering complex Spark optimisation, Unity Catalog, "
            "streaming architectures and enterprise-grade lakehouse governance. "
            "Ideal for senior data engineers working in large-scale Databricks environments."
        ),
        "tags": "Databricks,Spark,Unity Catalog,streaming,advanced,lakehouse",
        "link_oficial": "https://www.databricks.com/learn/certification/data-engineer-professional",
        "link_curso": "",
    },
    # ── Foundations ───────────────────────────────────────────────────────────
    {
        "titulo": "Google Data Analytics Professional Certificate",
        "fornecedor": "Google / Coursera",
        "categoria": "Beginner / Foundations",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "descricao": (
            "A comprehensive entry-level program covering data analysis, SQL, R, "
            "spreadsheets, Tableau and the full analytics workflow. "
            "Great starting point for anyone entering the data field."
        ),
        "tags": "analytics,SQL,R,Tableau,foundations,beginner,Coursera",
        "link_oficial": "https://www.coursera.org/professional-certificates/google-data-analytics",
        "link_curso": "",
    },
    {
        "titulo": "CompTIA Data+",
        "fornecedor": "CompTIA",
        "categoria": "Beginner / Foundations",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "descricao": (
            "Vendor-neutral certification validating core data concepts: data concepts, "
            "mining, analysis, visualisation and governance. Good vendor-agnostic foundation "
            "for early-career data professionals."
        ),
        "tags": "foundations,data concepts,analytics,governance,vendor-neutral,beginner",
        "link_oficial": "https://www.comptia.org/certifications/data",
        "link_curso": "",
    },
]


def seed_certifications(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        for cert in CERTIFICATIONS:
            cursor.execute("""
                INSERT INTO certifications
                    (titulo, fornecedor, categoria, nivel, prioridade, descricao, tags,
                     link_oficial, link_curso, ativo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW())
                ON CONFLICT DO NOTHING
            """, [
                cert["titulo"], cert["fornecedor"], cert["categoria"],
                cert["nivel"], cert["prioridade"], cert["descricao"],
                cert["tags"], cert["link_oficial"], cert["link_curso"],
            ])


def unseed_certifications(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM certifications WHERE titulo = ANY(%s)", [
            [c["titulo"] for c in CERTIFICATIONS]
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_add_certifications'),
    ]

    operations = [
        migrations.RunPython(seed_certifications, reverse_code=unseed_certifications),
    ]
