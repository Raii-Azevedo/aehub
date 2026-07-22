from django.db import migrations


# Sourced from the "AE Suggested Certifications List.xlsx" spreadsheet.
# Entries that already exist in the catalog (e.g. Microsoft PL-300, DP-600,
# SnowPro Core, AWS Data Engineer Associate, Google Professional Data Engineer,
# Tableau Certified Data Analyst, Databricks Data Engineer Professional) were
# left out to avoid duplicates.
CERTIFICATIONS = [
    {
        "titulo": "Microsoft Certified: AZ-900 (Azure Fundamentals)",
        "fornecedor": "Microsoft",
        "categoria": "Beginner / Foundations",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Entry point into the Microsoft Azure ecosystem: core cloud concepts, "
            "Azure services, pricing and support. A common first step before any "
            "Azure data or AI certification."
        ),
        "tags": "Azure,cloud,foundations,Microsoft",
        "link_oficial": "https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/",
        "link_curso": "https://esi.microsoft.com/landing",
    },
    {
        "titulo": "Microsoft Certified: DP-900 (Azure Data Fundamentals)",
        "fornecedor": "Microsoft",
        "categoria": "Beginner / Foundations",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Covers core data concepts and how they map to Azure data services: "
            "relational, non-relational, and analytics workloads. Good foundation "
            "before pursuing DP-600 or other Azure data certifications."
        ),
        "tags": "Azure,data fundamentals,foundations,Microsoft",
        "link_oficial": "https://learn.microsoft.com/en-us/credentials/certifications/azure-data-fundamentals/",
        "link_curso": "https://esi.microsoft.com/landing",
    },
    {
        "titulo": "Microsoft Certified: AI-900 (Azure AI Fundamentals)",
        "fornecedor": "Microsoft",
        "categoria": "AI & Data Platform",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Introduces AI and machine learning concepts and how they're implemented "
            "through Azure AI services and Azure Machine Learning. A gentle entry "
            "point into AI & Advanced Analytics."
        ),
        "tags": "Azure,AI,machine learning,foundations,Microsoft",
        "link_oficial": "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/",
        "link_curso": "https://esi.microsoft.com/landing",
    },
    {
        "titulo": "Microsoft Certified: PL-900 (Power Platform Fundamentals)",
        "fornecedor": "Microsoft",
        "categoria": "BI & Visualization",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Covers the business value and core components of Power Platform "
            "(Power BI, Power Apps, Power Automate, Power Virtual Agents). "
            "Useful foundation before PL-300."
        ),
        "tags": "Power Platform,Power BI,foundations,Microsoft",
        "link_oficial": "https://learn.microsoft.com/en-us/credentials/certifications/power-platform-fundamentals/",
        "link_curso": "https://esi.microsoft.com/landing",
    },
    {
        "titulo": "Microsoft Certified: Azure Solutions Architect Expert",
        "fornecedor": "Microsoft",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Advanced",
        "prioridade": "complementary",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Expert-level certification covering end-to-end Azure solution design: "
            "compute, network, storage and security architecture. Strong "
            "differentiator for AEs moving toward cloud/data architecture roles."
        ),
        "tags": "Azure,cloud architecture,expert,Microsoft",
        "link_oficial": "https://learn.microsoft.com/en-us/credentials/certifications/azure-solutions-architect/",
        "link_curso": "https://esi.microsoft.com/landing",
    },
    {
        "titulo": "Google Cloud Digital Leader",
        "fornecedor": "Google Cloud",
        "categoria": "Beginner / Foundations",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Vendor-level foundation covering Google Cloud's core products and how "
            "organisations use them to achieve business goals. No hands-on "
            "technical work required — a good non-technical starting point."
        ),
        "tags": "Google Cloud,foundations,business",
        "link_oficial": "https://cloud.google.com/learn/certification/cloud-digital-leader",
        "link_curso": "https://cloud.google.com/training/business",
    },
    {
        "titulo": "Google UX Design Professional",
        "fornecedor": "Google",
        "categoria": "BI & Visualization",
        "nivel": "Beginner",
        "prioridade": "complementary",
        "tipo_certificacao": "free_course",
        "descricao": (
            "Covers UX research, wireframing, prototyping and usability testing. "
            "A useful complementary skill for AEs who design dashboards and "
            "data products end users interact with directly."
        ),
        "tags": "UX,design,dashboards,storytelling",
        "link_oficial": "https://www.coursera.org/professional-certificates/google-ux-design",
        "link_curso": "https://www.coursera.org/professional-certificates/google-ux-design",
    },
    {
        "titulo": "Google Associate Data Practitioner",
        "fornecedor": "Google Cloud",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Intermediate",
        "prioridade": "foundations",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Validates the ability to harness data using Google Cloud tools: "
            "data preparation, pipeline building, analysis and basic ML. "
            "A practical step up from Cloud Digital Leader."
        ),
        "tags": "Google Cloud,data pipelines,foundations",
        "link_oficial": "https://cloud.google.com/learn/certification/data-practitioner",
        "link_curso": "https://cloud.google.com/training/data-management",
    },
    {
        "titulo": "Google Professional ML Engineer",
        "fornecedor": "Google Cloud",
        "categoria": "AI & Data Platform",
        "nivel": "Advanced",
        "prioridade": "recommended",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Advanced certification covering the design, build and productionisation "
            "of ML models on Google Cloud (Vertex AI, MLOps, feature engineering). "
            "Strong signal for AEs moving into AI & Advanced Analytics."
        ),
        "tags": "Google Cloud,machine learning,Vertex AI,MLOps",
        "link_oficial": "https://cloud.google.com/learn/certification/machine-learning-engineer",
        "link_curso": "https://cloud.google.com/training/machinelearning-ai",
    },
    {
        "titulo": "AWS Certified Cloud Practitioner (CLF-C02)",
        "fornecedor": "Amazon Web Services",
        "categoria": "Beginner / Foundations",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Entry-level, vendor-level overview of AWS cloud concepts, core services, "
            "security and pricing. Recommended first step before any AWS data "
            "certification."
        ),
        "tags": "AWS,cloud,foundations",
        "link_oficial": "https://aws.amazon.com/certification/certified-cloud-practitioner/",
        "link_curso": "https://skillbuilder.aws/",
    },
    {
        "titulo": "AWS Certified Machine Learning - Specialty",
        "fornecedor": "Amazon Web Services",
        "categoria": "AI & Data Platform",
        "nivel": "Advanced",
        "prioridade": "recommended",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Specialty-level certification covering ML modelling, data engineering "
            "for ML, and deployment/operationalisation on AWS (SageMaker and related "
            "services). Advanced signal for AI & Advanced Analytics work."
        ),
        "tags": "AWS,machine learning,SageMaker,advanced",
        "link_oficial": "https://aws.amazon.com/certification/certified-machine-learning-specialty/",
        "link_curso": "https://skillbuilder.aws/",
    },
    {
        "titulo": "Databricks Fundamentals (Core, AI, Agents)",
        "fornecedor": "Databricks",
        "categoria": "Beginner / Foundations",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "tipo_certificacao": "free_course",
        "descricao": (
            "Free introductory course set covering the Databricks Lakehouse "
            "platform, plus AI and agent-building basics. Good starting point "
            "before pursuing paid Databricks certifications."
        ),
        "tags": "Databricks,lakehouse,foundations,free",
        "link_oficial": "https://partner-academy.databricks.com/",
        "link_curso": "https://partner-academy.databricks.com/",
    },
    {
        "titulo": "Databricks Certified Data Analyst Associate",
        "fornecedor": "Databricks",
        "categoria": "BI & Visualization",
        "nivel": "Intermediate",
        "prioridade": "recommended",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Validates the ability to use Databricks SQL and dashboards for data "
            "analysis and visualisation on the Lakehouse. Relevant for AEs doing "
            "BI work on top of Databricks."
        ),
        "tags": "Databricks,SQL,dashboards,BI",
        "link_oficial": "https://www.databricks.com/learn/certification/data-analyst-associate",
        "link_curso": "https://partner-academy.databricks.com/",
    },
    {
        "titulo": "Databricks GenAI Engineer Associate",
        "fornecedor": "Databricks",
        "categoria": "AI & Data Platform",
        "nivel": "Intermediate",
        "prioridade": "recommended",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Covers building and deploying generative AI applications on Databricks: "
            "RAG pipelines, prompt engineering, model serving and evaluation. "
            "Timely certification for GenAI-focused analytics engineering work."
        ),
        "tags": "Databricks,GenAI,RAG,LLM",
        "link_oficial": "https://www.databricks.com/learn/certification/genai-engineer-associate",
        "link_curso": "https://partner-academy.databricks.com/",
    },
    {
        "titulo": "dbt Fundamentals",
        "fornecedor": "dbt Labs",
        "categoria": "Beginner / Foundations",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "tipo_certificacao": "free_course",
        "descricao": (
            "Free introductory course covering dbt's core concepts: models, tests, "
            "documentation and the ELT workflow. Recommended starting point before "
            "the dbt Analytics Engineering Certification."
        ),
        "tags": "dbt,ELT,foundations,free",
        "link_oficial": "https://courses.getdbt.com/courses/fundamentals",
        "link_curso": "https://courses.getdbt.com/courses/fundamentals",
    },
    {
        "titulo": "dbt Analytics Engineering Certification",
        "fornecedor": "dbt Labs",
        "categoria": "Analytics Engineering / Modern Data Stack",
        "nivel": "Intermediate",
        "prioridade": "must_have",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Official dbt certification validating core analytics engineering "
            "skills: modelling, testing, documentation and deployment. Considered "
            "near-mandatory for AEs working with dbt."
        ),
        "tags": "dbt,analytics engineering,ELT,data modeling",
        "link_oficial": "https://www.getdbt.com/dbt-assets/certifications/dbt-certificate-study-guide",
        "link_curso": "https://courses.getdbt.com/courses/dbt-certified-developer-path",
    },
    {
        "titulo": "dbt Architect Certification",
        "fornecedor": "dbt Labs",
        "categoria": "Analytics Engineering / Modern Data Stack",
        "nivel": "Advanced",
        "prioridade": "complementary",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Advanced dbt certification covering project architecture, governance, "
            "performance and team workflows at scale. A strong differentiator for "
            "senior AEs owning the dbt project structure."
        ),
        "tags": "dbt,architecture,governance,advanced",
        "link_oficial": "https://www.getdbt.com/certifications/dbt-architect",
        "link_curso": "https://courses.getdbt.com/courses/dbt-certified-architect-path",
    },
    {
        "titulo": "SnowPro Advanced: Architect",
        "fornecedor": "Snowflake",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Advanced",
        "prioridade": "complementary",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Advanced Snowflake certification covering platform architecture, "
            "security design, data sharing and performance at scale. Builds on "
            "SnowPro Core for architecture-focused roles."
        ),
        "tags": "Snowflake,architecture,advanced,cloud",
        "link_oficial": "https://www.snowflake.com/en/learn/certification/snowpro-advanced-architect/",
        "link_curso": "https://learn.snowflake.com/",
    },
    {
        "titulo": "SnowPro Advanced: Data Engineer",
        "fornecedor": "Snowflake",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Advanced",
        "prioridade": "complementary",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Advanced Snowflake certification focused on data pipeline design, "
            "performance optimisation and orchestration within Snowflake. Builds "
            "on SnowPro Core for engineering-focused roles."
        ),
        "tags": "Snowflake,data engineering,pipelines,advanced",
        "link_oficial": "https://www.snowflake.com/en/learn/certification/snowpro-advanced-data-engineer/",
        "link_curso": "https://learn.snowflake.com/",
    },
    {
        "titulo": "Tableau Desktop Specialist",
        "fornecedor": "Tableau (Salesforce)",
        "categoria": "BI & Visualization",
        "nivel": "Beginner",
        "prioridade": "foundations",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Entry-level Tableau certification covering core product knowledge: "
            "connecting to data, building basic visualisations, and navigating "
            "the interface. Recommended before Tableau Certified Data Analyst."
        ),
        "tags": "Tableau,visualization,foundations,BI",
        "link_oficial": "https://www.tableau.com/learn/certification/desktop-specialist",
        "link_curso": "https://trailhead.salesforce.com/",
    },
    {
        "titulo": "Salesforce Data Cloud Consultant",
        "fornecedor": "Salesforce",
        "categoria": "Cloud & Data Engineering",
        "nivel": "Advanced",
        "prioridade": "complementary",
        "tipo_certificacao": "paid_exam",
        "descricao": (
            "Covers designing and implementing Salesforce Data Cloud solutions: "
            "data harmonisation, identity resolution and activation. Relevant for "
            "AEs working on customer data platform / agentic data initiatives."
        ),
        "tags": "Salesforce,Data Cloud,CDP,advanced",
        "link_oficial": "https://trailhead.salesforce.com/credentials/datacloudconsultant",
        "link_curso": "https://trailhead.salesforce.com/",
    },
]


def seed_certifications(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        for cert in CERTIFICATIONS:
            cursor.execute("""
                INSERT INTO certifications
                    (titulo, fornecedor, categoria, nivel, prioridade, tipo_certificacao,
                     descricao, tags, link_oficial, link_curso, ativo, data_criacao)
                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM certifications WHERE titulo = %s
                )
            """, [
                cert["titulo"], cert["fornecedor"], cert["categoria"],
                cert["nivel"], cert["prioridade"], cert["tipo_certificacao"],
                cert["descricao"], cert["tags"], cert["link_oficial"], cert["link_curso"],
                cert["titulo"],
            ])


def unseed_certifications(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM certifications WHERE titulo = ANY(%s)", [
            [c["titulo"] for c in CERTIFICATIONS]
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_certification_level_and_type'),
    ]

    operations = [
        migrations.RunPython(seed_certifications, reverse_code=unseed_certifications),
    ]
