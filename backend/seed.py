"""Seed database with initial certification data."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.provider import Provider
from app.models.certification import Certification, ExamVersion, ExamVersionStatus
from app.models.domain import Domain
from app.models.topic import Topic
from app.models.concept import Concept, ConceptDifficulty
from app.models.question import Question, QuestionOption, QuestionType, AccessLevel, QuestionDifficulty
from app.models.learning_resource import LearningResource, ResourceType
from app.models.flashcard import Flashcard
from app.models.product import Product, ProductType
from app.models.career import CareerPath, CareerCertification
from app.models.achievement import Achievement, UserGamification
from app.models.content_version import ContentVersion
from app.auth import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # --- Users ---
        admin = db.query(User).filter(User.email == "admin@niksmind.com").first()
        if not admin:
            admin = User(
                name="Admin",
                email="admin@niksmind.com",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
            )
            db.add(admin)

        demo = db.query(User).filter(User.email == "demo@niksmind.com").first()
        if not demo:
            demo = User(
                name="Demo User",
                email="demo@niksmind.com",
                password_hash=hash_password("demo123"),
                role=UserRole.USER,
            )
            db.add(demo)

        db.flush()

        # --- Providers ---
        providers = {}
        for p_data in [
            ("Microsoft", "microsoft", "https://learn.microsoft.com"),
            ("AWS", "aws", "https://aws.amazon.com/certification/"),
            ("Cisco", "cisco", "https://www.cisco.com/c/en/us/training-events.html"),
            ("CompTIA", "comptia", "https://www.comptia.org/certifications"),
        ]:
            p = db.query(Provider).filter(Provider.slug == p_data[1]).first()
            if not p:
                p = Provider(name=p_data[0], slug=p_data[1], website_url=p_data[2])
                db.add(p)
            providers[p_data[1]] = p
        db.flush()

        # ============================================================
        # AZ-900
        # ============================================================
        az900 = db.query(Certification).filter(Certification.slug == "az-900").first()
        if not az900:
            az900 = Certification(
                provider_id=providers["microsoft"].id,
                name="Azure Fundamentals",
                slug="az-900",
                code="AZ-900",
                description="This certification validates foundational knowledge of cloud services and how those services are provided with Microsoft Azure.",
                level="beginner",
                category="cloud",
                estimated_hours=20,
            )
            db.add(az900)
            db.flush()

            # Exam Version
            ev = ExamVersion(
                certification_id=az900.id,
                version="2026",
                effective_date=datetime(2025, 1, 1),
                status=ExamVersionStatus.ACTIVE,
            )
            db.add(ev)
            db.flush()

            # Product
            product = Product(
                name="AZ-900 Premium",
                slug="az-900-premium",
                description="Unlock 50 premium MCQs per topic, mock exams, AI tutor, flashcards, and adaptive learning for AZ-900.",
                certification_id=az900.id,
                price=499.0,
                currency="INR",
                product_type=ProductType.CERTIFICATION,
            )
            db.add(product)

            # --- Domains ---
            domains_data = [
                ("Cloud Concepts", "Describe cloud computing and the Azure environment.", 25, 1),
                ("Azure Architecture and Services", "Describe the core architectural components of Azure.", 35, 2),
                ("Management and Governance", "Describe the management and governance tools and features in Azure.", 20, 3),
                ("Security, Privacy, Compliance, and Trust", "Describe security, privacy, compliance, and trust features in Azure.", 20, 4),
            ]

            domain_ids = {}
            for d_name, d_desc, d_weight, d_order in domains_data:
                d = Domain(
                    exam_version_id=ev.id,
                    name=d_name,
                    description=d_desc,
                    weight_percentage=d_weight,
                    order_index=d_order,
                )
                db.add(d)
                db.flush()
                domain_ids[d_name] = d.id

            # --- Topics ---
            topics_map = {}

            # Cloud Concepts topics
            cc_topics = [
                ("What is Cloud Computing", "what-is-cloud-computing", "Understanding cloud computing fundamentals"),
                ("Benefits of Cloud", "benefits-of-cloud", "Benefits of using cloud services"),
                ("Cloud Models", "cloud-models", "Public, private, and hybrid cloud models"),
                ("Shared Responsibility Model", "shared-responsibility-model", "Cloud responsibility model"),
            ]
            for i, (t_name, t_slug, t_desc) in enumerate(cc_topics):
                t = Topic(domain_id=domain_ids["Cloud Concepts"], name=t_name, slug=t_slug, description=t_desc, order_index=i+1)
                db.add(t)
                db.flush()
                topics_map[t_slug] = t.id

            # Azure Architecture topics
            aa_topics = [
                ("Azure Compute", "azure-compute", "Virtual machines, containers, and serverless"),
                ("Azure Networking", "azure-networking", "Virtual networks, load balancing, and DNS"),
                ("Azure Storage", "azure-storage", "Blob, file, queue, and table storage"),
                ("Azure Databases", "azure-databases", "Azure SQL, Cosmos DB, and database services"),
                ("Azure Regions", "azure-regions", "Geography, regions, and availability zones"),
            ]
            for i, (t_name, t_slug, t_desc) in enumerate(aa_topics):
                t = Topic(domain_id=domain_ids["Azure Architecture and Services"], name=t_name, slug=t_slug, description=t_desc, order_index=i+1)
                db.add(t)
                db.flush()
                topics_map[t_slug] = t.id

            # Management and Governance topics
            mg_topics = [
                ("Cost Management", "cost-management", "Managing and optimizing Azure costs"),
                ("Tools for Azure Management", "azure-management-tools", "Azure portal, CLI, PowerShell, and ARM"),
                ("Azure Resource Manager", "azure-resource-manager", "ARM templates and resource groups"),
                ("Monitoring and Compliance", "monitoring-compliance", "Azure Monitor, Policy, and Blueprints"),
            ]
            for i, (t_name, t_slug, t_desc) in enumerate(mg_topics):
                t = Topic(domain_id=domain_ids["Management and Governance"], name=t_name, slug=t_slug, description=t_desc, order_index=i+1)
                db.add(t)
                db.flush()
                topics_map[t_slug] = t.id

            # Security topics
            sec_topics = [
                ("Zero Trust Model", "zero-trust-model", "Zero trust security model"),
                ("Defense in Depth", "defense-in-depth", "Layered security approach"),
                ("Microsoft Defender for Cloud", "defender-for-cloud", "Cloud security posture management"),
                ("Azure Key Vault", "azure-key-vault", "Secrets and key management"),
                ("Network Security", "network-security", "NSGs, firewalls, and DDoS protection"),
            ]
            for i, (t_name, t_slug, t_desc) in enumerate(sec_topics):
                t = Topic(domain_id=domain_ids["Security, Privacy, Compliance, and Trust"], name=t_name, slug=t_slug, description=t_desc, order_index=i+1)
                db.add(t)
                db.flush()
                topics_map[t_slug] = t.id

            # --- Concepts ---
            concepts_map = {}

            # Cloud Concepts
            concept_data = [
                ("what-is-cloud-computing", "Cloud Computing", "Cloud computing is the delivery of computing services over the internet.", "Cloud computing means using the internet to access and use computer resources like servers, storage, databases, and software instead of owning physical hardware.", "Cloud computing is the on-demand availability of computer system resources, especially data storage and computing power, without direct active management by the user. The term is generally used to describe data centers available to many users over the Internet.", "Instead of buying and maintaining your own servers, you rent computing power from providers like Azure. When you use Gmail, Netflix, or OneDrive, you're using cloud computing.", "On-demand self-service, Broad network access, Resource pooling, Rapid elasticity, Measured service.", "Think of cloud computing like electricity. You don't generate your own electricity; you pay a utility company. Similarly, you don't need to own servers; you rent compute from Azure.", "Confusing cloud computing with just 'the internet'. Cloud computing is specifically about computing services delivered over the internet."),
                ("benefits-of-cloud", "Benefits of Cloud Computing", "Key benefits include scalability, cost efficiency, reliability, and global reach.", "The main benefits of cloud computing include:\n\n• **Scalability**: Easily scale resources up or down based on demand.\n• **Cost Efficiency**: Pay only for what you use (OpEx vs CapEx).\n• **Reliability**: Data backup, disaster recovery, and high availability.\n• **Global Reach**: Deploy applications worldwide in minutes.\n• **Speed**: Rapid deployment of resources.\n• **Security**: Enterprise-grade security features.", "Cloud computing offers several key benefits that make it attractive to organizations of all sizes. Scalability allows businesses to handle varying workloads efficiently. Cost efficiency eliminates large upfront capital expenditures in favor of operational expenses. Reliability is ensured through built-in redundancy and disaster recovery capabilities. Global reach enables deployment across Microsoft's worldwide network of data centers.", "A startup can launch a global application on Azure without buying a single server. They start small and scale as they grow, paying only for what they use.", "Scalability, Cost efficiency, Reliability, Global reach, Speed, Security, Elasticity.", "Don't confuse OpEx with CapEx. Cloud converts CapEx (buying hardware) to OpEx (paying monthly).", "Thinking cloud always saves money. It can if managed well, but unoptimized cloud usage can be expensive."),
                ("cloud-models", "Cloud Deployment Models", "Public, private, and hybrid cloud models serve different needs.", "**Public Cloud**: Resources owned and operated by a third-party provider, shared among multiple organizations. Example: Azure, AWS.\n\n**Private Cloud**: Computing services used exclusively by a single organization. Can be on-premises or hosted.\n\n**Hybrid Cloud**: Combination of public and private clouds, allowing data and applications to be shared between them.", "Public cloud is like living in an apartment building — you share infrastructure but have your own space. Private cloud is like having your own house — dedicated to you. Hybrid cloud is like having a house with access to shared community facilities.", "The public cloud model provides computing resources over the internet, shared among multiple tenants. Private cloud is dedicated to a single organization. Hybrid cloud combines both, enabling workload portability between environments.", "Many enterprises use hybrid cloud: keeping sensitive data in a private cloud while using Azure public cloud for less sensitive workloads.", "Public, Private, Hybrid.", "Don't confuse hybrid cloud with multi-cloud. Multi-cloud uses multiple public cloud providers.", "Confusing 'hybrid' with 'multi-cloud'. Hybrid = public + private. Multi-cloud = multiple public providers."),
                ("shared-responsibility-model", "Shared Responsibility Model", "Security responsibilities are shared between cloud provider and customer.", "**In IaaS**: Microsoft manages physical infrastructure; you manage OS, data, applications.\n**In PaaS**: Microsoft manages OS, runtime; you manage data and applications.\n**In SaaS**: Microsoft manages everything; you manage users and data access.", "Think of it like renting an apartment. The landlord (cloud provider) maintains the building structure, utilities, and security. You (customer) are responsible for what's inside your apartment — your furniture, locks, and who you give keys to.", "The shared responsibility model defines which security tasks belong to the cloud provider versus the customer. As you move from IaaS to PaaS to SaaS, the provider takes on more responsibility.", "In Azure SaaS (like Microsoft 365), Microsoft manages almost everything. You're responsible for managing user access and ensuring the right people have access to data.", "In SaaS: Customer = data + access. In IaaS: Customer = OS + data + network. In PaaS: Customer = data + applications.", "Remember: Customer always manages data, identity, and on-premises resources regardless of service model.", "Thinking the provider is responsible for everything in SaaS. Customer still manages data classification, users, and access."),
            ]

            for topic_slug, concept_name, short_def, simple_exp, detailed_exp, examples, key_pts, tips, mistakes in concept_data:
                topic_id = topics_map.get(topic_slug)
                if not topic_id:
                    continue
                c = Concept(
                    topic_id=topic_id,
                    name=concept_name,
                    slug=concept_name.lower().replace(" ", "-"),
                    short_definition=short_def,
                    simple_explanation=simple_exp,
                    detailed_explanation=detailed_exp,
                    examples=examples,
                    key_points=key_pts,
                    exam_tips=tips,
                    common_mistakes=mistakes,
                    difficulty=ConceptDifficulty.MEDIUM,
                )
                db.add(c)
                db.flush()
                concepts_map[topic_slug] = c.id

            # --- Questions (Free - 5 per topic sample) ---
            questions_data = [
                # Cloud Computing
                ("what-is-cloud-computing", "Which of the following best defines cloud computing?", "The delivery of computing services over the internet", "Storing data on a local hard drive", "Using a VPN to access the internet", "Downloading software from a website", 0, "Cloud computing is the delivery of computing services including servers, storage, databases, networking, software, and analytics over the internet.", QuestionDifficulty.EASY),
                ("what-is-cloud-computing", "Which of the following is NOT a characteristic of cloud computing?", "Requires physical hardware ownership", "On-demand self-service", "Broad network access", "Measured service", 0, "Cloud computing eliminates the need for physical hardware ownership. Users access resources on-demand over the internet.", QuestionDifficulty.MEDIUM),
                ("what-is-cloud-computing", "Cloud computing follows which service model where users pay only for what they use?", "Measured service", "Resource pooling", "Rapid elasticity", "On-demand self-service", 0, "Measured service means cloud resources are monitored and billed based on actual usage.", QuestionDifficulty.EASY),
                ("what-is-cloud-computing", "Which cloud service model provides the MOST control to the customer?", "Infrastructure as a Service (IaaS)", "Software as a Service (SaaS)", "Platform as a Service (PaaS)", "Function as a Service (FaaS)", 0, "IaaS gives customers the most control over infrastructure, including OS, networking, and storage.", QuestionDifficulty.MEDIUM),
                ("what-is-cloud-computing", "What does 'elasticity' mean in cloud computing?", "The ability to automatically scale resources based on demand", "The physical security of data centers", "The encryption of data in transit", "The ability to run multiple OS on one server", 0, "Elasticity refers to the cloud's ability to automatically provision and deprovision resources as demand changes.", QuestionDifficulty.MEDIUM),

                # Benefits of Cloud
                ("benefits-of-cloud", "Which benefit of cloud computing eliminates large upfront capital expenditures?", "Pay-as-you-go pricing", "Global reach", "High availability", "Scalability", 0, "Pay-as-you-go converts CapEx to OpEx, eliminating the need for large upfront hardware investments.", QuestionDifficulty.EASY),
                ("benefits-of-cloud", "A company needs to handle a sudden traffic spike. Which cloud benefit helps?", "Scalability", "Cost efficiency", "Compliance", "Governance", 0, "Scalability allows resources to be increased or decreased based on demand.", QuestionDifficulty.EASY),
                ("benefits-of-cloud", "Which cloud benefit ensures your application remains available during hardware failures?", "Reliability", "Agility", "Elasticity", "Global reach", 0, "Reliability includes built-in redundancy, failover, and disaster recovery capabilities.", QuestionDifficulty.MEDIUM),
                ("benefits-of-cloud", "What does 'OpEx' stand for in cloud cost management?", "Operational Expenditure", "Optimized Experience", "Online Performance Execution", "Open External Process", 0, "OpEx (Operational Expenditure) refers to ongoing costs for using services, as opposed to CapEx (Capital Expenditure) for buying assets.", QuestionDifficulty.EASY),
                ("benefits-of-cloud", "Which of the following is a benefit of cloud computing for a startup?", "Deploy globally without buying physical servers", "Must purchase servers in each region", "Requires large IT staff", "Long deployment cycles", 0, "Cloud computing allows startups to deploy globally without investing in physical infrastructure.", QuestionDifficulty.EASY),

                # Cloud Models
                ("cloud-models", "Which cloud deployment model is exclusive to a single organization?", "Private cloud", "Public cloud", "Hybrid cloud", "Community cloud", 0, "A private cloud is dedicated to a single organization and is not shared with others.", QuestionDifficulty.EASY),
                ("cloud-models", "A company uses Azure for non-sensitive workloads and a private cloud for sensitive data. This is:", "Hybrid cloud", "Public cloud", "Private cloud", "Multi-cloud", 0, "Hybrid cloud combines public and private cloud environments, allowing workload portability.", QuestionDifficulty.MEDIUM),
                ("cloud-models", "Which cloud model provides the LOWEST upfront cost?", "Public cloud", "Private cloud", "On-premises", "Dedicated hosting", 0, "Public cloud has the lowest upfront cost as resources are shared and pay-as-you-go.", QuestionDifficulty.EASY),
                ("cloud-models", "Using both Azure and AWS simultaneously is an example of:", "Multi-cloud", "Hybrid cloud", "Private cloud", "Community cloud", 0, "Multi-cloud refers to using multiple public cloud providers simultaneously.", QuestionDifficulty.MEDIUM),
                ("cloud-models", "Which cloud model offers the MOST control over hardware and security?", "Private cloud", "Public cloud", "SaaS", "PaaS", 0, "Private cloud gives organizations complete control over their infrastructure and security configurations.", QuestionDifficulty.MEDIUM),

                # Shared Responsibility
                ("shared-responsibility-model", "In an IaaS model, who is responsible for managing the operating system?", "The customer", "Microsoft", "The network provider", "The data center owner", 0, "In IaaS, the customer is responsible for the OS, applications, data, and middleware.", QuestionDifficulty.EASY),
                ("shared-responsibility-model", "In SaaS, which of the following is the CUSTOMER responsible for?", "Data classification and user access", "Physical security of data centers", "Network infrastructure", "Operating system patching", 0, "In SaaS, customers are responsible for data classification, user access management, and data governance.", QuestionDifficulty.MEDIUM),
                ("shared-responsibility-model", "Who is responsible for physical security in all cloud service models?", "The cloud provider", "The customer", "Both shared equally", "The network administrator", 0, "The cloud provider is always responsible for physical data center security.", QuestionDifficulty.EASY),
                ("shared-responsibility-model", "In PaaS, what does the customer manage?", "Data and applications", "Operating system and runtime", "Physical servers", "Network switches", 0, "In PaaS, the customer manages data and applications while the provider handles OS, runtime, and infrastructure.", QuestionDifficulty.MEDIUM),
                ("shared-responsibility-model", "As you move from IaaS to SaaS, what happens to provider responsibility?", "It increases", "It decreases", "It stays the same", "It becomes optional", 0, "Moving from IaaS to PaaS to SaaS, the provider takes on more responsibility for managing the stack.", QuestionDifficulty.EASY),

                # Azure Compute
                ("azure-compute", "Which Azure service provides fully managed virtual machines?", "Azure Virtual Machines", "Azure App Service", "Azure Functions", "Azure Container Instances", 0, "Azure Virtual Machines provide IaaS compute with full control over the operating system.", QuestionDifficulty.EASY),
                ("azure-compute", "Which compute service is best for running a web application without managing servers?", "Azure App Service", "Azure Virtual Machines", "Azure Batch", "Azure Dedicated Host", 0, "Azure App Service is a PaaS offering ideal for hosting web apps without managing infrastructure.", QuestionDifficulty.MEDIUM),
                ("azure-compute", "Azure Functions is an example of which computing model?", "Serverless / FaaS", "IaaS", "PaaS", "Dedicated hosting", 0, "Azure Functions provides serverless compute, executing code in response to events without managing servers.", QuestionDifficulty.MEDIUM),
                ("azure-compute", "Which service lets you run containers without managing the underlying infrastructure?", "Azure Container Instances", "Azure Kubernetes Service", "Azure Virtual Machines", "Azure Batch", 0, "ACI provides serverless containers, running containers without managing VMs or orchestrators.", QuestionDifficulty.MEDIUM),
                ("azure-compute", "What is Azure Virtual Machine Scale Sets?", "Auto-scaling group of load-balanced VMs", "A single powerful VM", "A container orchestration service", "A serverless function", 0, "VM Scale Sets automatically increase or decrease the number of VM instances based on demand.", QuestionDifficulty.HARD),

                # Azure Networking
                ("azure-networking", "What is an Azure Virtual Network (VNet)?", "A logically isolated network in Azure", "A physical network cable", "An internet connection", "A VPN to on-premises", 0, "A VNet is a logically isolated section of the Azure network for deploying Azure resources.", QuestionDifficulty.EASY),
                ("azure-networking", "Which service distributes incoming traffic across multiple VMs?", "Azure Load Balancer", "Azure CDN", "Azure Traffic Manager", "Azure Front Door", 0, "Azure Load Balancer distributes incoming traffic among healthy service instances in a pool of VMs.", QuestionDifficulty.MEDIUM),
                ("azure-networking", "What is the purpose of Azure DNS?", "To host DNS domains and provide name resolution", "To manage network security groups", "To create virtual networks", "To configure VPN gateways", 0, "Azure DNS hosts DNS domains and provides name resolution using Microsoft Azure infrastructure.", QuestionDifficulty.MEDIUM),
                ("azure-networking", "Which service provides DDoS protection for Azure resources?", "Azure DDoS Protection", "Azure Firewall", "Network Security Group", "Azure WAF", 0, "Azure DDoS Protection provides enhanced mitigation for DDoS attacks against Azure resources.", QuestionDifficulty.MEDIUM),
                ("azure-networking", "What is a Network Security Group (NSG)?", "A list of security rules allowing/denying network traffic", "A physical firewall appliance", "A VPN configuration", "A load balancer rule set", 0, "NSGs contain security rules that allow or deny traffic to and from Azure resources based on source/destination.", QuestionDifficulty.MEDIUM),

                # Azure Storage
                ("azure-storage", "Which Azure storage service stores unstructured data like images and videos?", "Blob Storage", "File Storage", "Queue Storage", "Table Storage", 0, "Blob Storage is optimized for storing massive amounts of unstructured data.", QuestionDifficulty.EASY),
                ("azure-storage", "What are the three Blob storage access tiers?", "Hot, Cool, and Archive", "Basic, Standard, and Premium", "Read, Write, and Delete", "Local, Regional, and Global", 0, "Hot for frequent access, Cool for infrequent access, Archive for rarely accessed data.", QuestionDifficulty.MEDIUM),
                ("azure-storage", "Which storage service provides SMB file shares in Azure?", "Azure Files", "Blob Storage", "Queue Storage", "Data Lake Storage", 0, "Azure Files offers fully managed file shares accessible via SMB protocol.", QuestionDifficulty.MEDIUM),
                ("azure-storage", "What is the maximum size of a single Block Blob?", "190.7 TB", "1 TB", "8 TB", "500 GB", 0, "Block Blobs can be up to approximately 190.7 TB (4000 GB × 50,000 blocks).", QuestionDifficulty.HARD),
                ("azure-storage", "Which storage service provides messaging between application components?", "Queue Storage", "Blob Storage", "File Storage", "Disk Storage", 0, "Queue Storage provides reliable messaging between application components for async processing.", QuestionDifficulty.MEDIUM),

                # Azure Databases
                ("azure-databases", "Which Azure database service is a fully managed relational database?", "Azure SQL Database", "Azure Cosmos DB", "Azure Cache for Redis", "Azure Table Storage", 0, "Azure SQL Database is a fully managed relational database based on SQL Server.", QuestionDifficulty.EASY),
                ("azure-databases", "Azure Cosmos DB supports which type of database models?", "Multi-model (document, key-value, graph, column-family)", "Relational only", "NoSQL only", "Document only", 0, "Cosmos DB is a multi-model database supporting document, key-value, graph, and column-family models.", QuestionDifficulty.MEDIUM),
                ("azure-databases", "What is the key feature of Azure Cosmos DB for global applications?", "Multi-region writes with single-digit millisecond latency", "Only single-region deployment", "No replication capability", "Manual failover only", 0, "Cosmos DB provides turnkey global distribution with multi-region writes and low latency.", QuestionDifficulty.HARD),
                ("azure-databases", "Which Azure service provides in-memory caching for databases?", "Azure Cache for Redis", "Azure SQL Database", "Azure Cosmos DB", "Azure Data Lake", 0, "Azure Cache for Redis provides a fully managed Redis cache for high-performance data access.", QuestionDifficulty.MEDIUM),
                ("azure-databases", "What type of database is Azure SQL Managed Instance?", "Managed SQL Server instance (PaaS)", "NoSQL document database", "In-memory cache", "Graph database", 0, "SQL Managed Instance is a fully managed SQL Server instance with near-100% SQL Server compatibility.", QuestionDifficulty.HARD),

                # Azure Regions
                ("azure-regions", "What is an Azure region?", "A geographical area containing multiple data centers", "A single data center", "A virtual network", "An availability zone", 0, "An Azure region is a set of data centers deployed within a latency-defined perimeter and connected through a regional network.", QuestionDifficulty.EASY),
                ("azure-regions", "What is an Azure Availability Zone?", "A physically separate data center within an Azure region", "A geographic region", "A logical network", "A backup location", 0, "Availability Zones are physically separate locations within an Azure region, providing high availability.", QuestionDifficulty.MEDIUM),
                ("azure-regions", "Which Azure service provides geo-redundant storage?", "Azure Storage with GRS", "Azure CDN", "Azure Traffic Manager", "Azure Front Door", 0, "Geo-Redundant Storage (GRS) replicates data to a secondary region hundreds of miles away.", QuestionDifficulty.MEDIUM),
                ("azure-regions", "What is Azure paired regions?", "Two regions in the same geography connected for disaster recovery", "Two data centers in the same building", "Two virtual networks in the same region", "Two subscriptions connected together", 0, "Paired regions are in the same geography and provide regional resiliency for services.", QuestionDifficulty.MEDIUM),
                ("azure-regions", "When deploying resources, which factor determines region selection?", "Data residency requirements and latency", "Only the cheapest region", "The region with the most VMs", "The first region alphabetically", 0, "Region selection should consider data residency, compliance, latency, and feature availability.", QuestionDifficulty.HARD),

                # Cost Management
                ("cost-management", "What tool does Azure provide for monitoring and managing costs?", "Azure Cost Management", "Azure Monitor", "Azure Advisor", "Azure Policy", 0, "Azure Cost Management provides tools to monitor, allocate, and optimize cloud costs.", QuestionDifficulty.EASY),
                ("cost-management", "Which Azure service recommends cost optimizations?", "Azure Advisor", "Azure Monitor", "Azure Cost Management", "Azure Policy", 0, "Azure Advisor provides personalized recommendations for cost, performance, reliability, and security.", QuestionDifficulty.MEDIUM),
                ("cost-management", "What is Azure Reserved Instances?", "Pre-purchased compute capacity at a discount", "A free tier for new users", "A type of virtual machine", "A storage tier", 0, "Reserved Instances allow you to pre-purchase VM capacity for 1 or 3 years at significant discounts.", QuestionDifficulty.MEDIUM),
                ("cost-management", "Which pricing calculator helps estimate Azure costs before deployment?", "Azure Pricing Calculator", "Azure Cost Management", "Azure Advisor", "Azure Monitor", 0, "The Azure Pricing Calculator estimates the cost of Azure services before you deploy them.", QuestionDifficulty.EASY),
                ("cost-management", "What does a tag help with in Azure cost management?", "Organizing and tracking resources for cost allocation", "Encrypting data", "Managing user access", "Deploying virtual machines", 0, "Tags help organize resources and track costs by department, project, or environment.", QuestionDifficulty.MEDIUM),

                # Management Tools
                ("azure-management-tools", "Which tool provides a web-based interface for managing Azure resources?", "Azure Portal", "Azure CLI", "Azure PowerShell", "Azure Cloud Shell", 0, "Azure Portal is a web-based console for managing all Azure resources.", QuestionDifficulty.EASY),
                ("azure-management-tools", "What is Azure Cloud Shell?", "A browser-based shell with Azure CLI and PowerShell", "A physical server in Azure", "A VPN client", "A database management tool", 0, "Cloud Shell is a free interactive shell that runs in the browser with pre-installed tools.", QuestionDifficulty.MEDIUM),
                ("azure-management-tools", "Which tool uses a command-line interface with task-automation capabilities?", "Azure CLI or Azure PowerShell", "Azure Portal only", "Visual Studio", "Azure DevOps", 0, "Both Azure CLI and Azure PowerShell provide command-line tools for managing Azure resources.", QuestionDifficulty.MEDIUM),
                ("azure-management-tools", "What is an ARM template?", "A JSON file that defines Azure resource configurations", "A PowerPoint template", "A network configuration file", "A storage container", 0, "ARM templates are declarative JSON files that define the infrastructure and configuration for Azure resources.", QuestionDifficulty.MEDIUM),
                ("azure-management-tools", "Azure Blueprint helps with:", "Setting up governance and compliance for Azure environments", "Creating network topologies", "Managing user passwords", "Deploying web applications", 0, "Azure Blueprints help define repeatable Azure environments that comply with organizational standards.", QuestionDifficulty.HARD),

                # Azure Resource Manager
                ("azure-resource-manager", "What is a resource group in Azure?", "A container for related Azure resources", "A type of virtual machine", "A network configuration", "A storage account", 0, "A resource group is a logical container for resources deployed on Azure.", QuestionDifficulty.EASY),
                ("azure-resource-manager", "What is Azure Resource Manager (ARM)?", "The deployment and management service for Azure", "A physical server management tool", "A backup service", "A networking tool", 0, "ARM is the deployment and management service that provides a management layer for creating, updating, and deleting resources.", QuestionDifficulty.MEDIUM),
                ("azure-resource-manager", "What language are ARM templates written in?", "JSON", "XML", "Python", "YAML", 0, "ARM templates are written in JSON format with a specific schema.", QuestionDifficulty.EASY),
                ("azure-resource-manager", "Which ARM feature allows you to track resources in a resource group?", "Resource locks", "Resource providers", "Deployments", "Tags", 0, "Resource locks prevent resources from being accidentally deleted or modified.", QuestionDifficulty.MEDIUM),
                ("azure-resource-manager", "What is the benefit of using ARM templates for deployment?", "Consistent, repeatable, and automated deployments", "Faster internet speed", "More storage capacity", "Better GPU performance", 0, "ARM templates enable Infrastructure as Code, allowing consistent and repeatable deployments.", QuestionDifficulty.MEDIUM),

                # Monitoring and Compliance
                ("monitoring-compliance", "What is Azure Monitor used for?", "Collecting, analyzing, and acting on telemetry data", "Only monitoring CPU usage", "Managing user accounts", "Deploying virtual machines", 0, "Azure Monitor collects, analyzes, and acts on telemetry from cloud and on-premises environments.", QuestionDifficulty.EASY),
                ("monitoring-compliance", "What is Azure Policy used for?", "Creating and enforcing organizational standards", "Monitoring network traffic", "Managing storage accounts", "Deploying applications", 0, "Azure Policy helps enforce organizational standards and assess compliance at scale.", QuestionDifficulty.MEDIUM),
                ("monitoring-compliance", "What does Azure Advisor provide?", "Personalized best practice recommendations", "Direct access to Microsoft support", "Free Azure credits", "Hardware diagnostics", 0, "Azure Advisor analyzes resource configurations and usage to recommend optimizations.", QuestionDifficulty.MEDIUM),
                ("monitoring-compliance", "Which service provides a compliance dashboard for Azure?", "Microsoft Purview Compliance Manager", "Azure Monitor", "Azure Cost Management", "Azure Portal", 0, "Compliance Manager provides a compliance dashboard with assessment and improvement actions.", QuestionDifficulty.HARD),
                ("monitoring-compliance", "What is Azure Service Health?", "A personalized dashboard tracking Azure service issues", "A tool for monitoring VM performance", "A compliance audit tool", "A network diagnostic tool", 0, "Azure Service Health provides information about current and upcoming issues in Azure services.", QuestionDifficulty.MEDIUM),

                # Zero Trust
                ("zero-trust-model", "What is the core principle of Zero Trust?", "Never trust, always verify", "Trust all internal traffic", "Trust but verify", "Encrypt everything", 0, "Zero Trust assumes breach and verifies each request as though it originates from an untrusted network.", QuestionDifficulty.EASY),
                ("zero-trust-model", "Which Zero Trust principle involves checking user identity continuously?", "Verify explicitly", "Use least privilege access", "Assume breach", "Encrypt data", 0, "Verify explicitly means always authenticating and authorizing based on all available data points.", QuestionDifficulty.MEDIUM),
                ("zero-trust-model", "Least privilege access means:", "Giving users only the minimum permissions needed", "Giving all users admin access", "Granting permanent access", "Sharing credentials", 0, "Least privilege limits access rights to only what is necessary for a user's job function.", QuestionDifficulty.EASY),
                ("zero-trust-model", "In Zero Trust, what does 'assume breach' mean?", "Minimize blast radius and segment access", "Assume all users are trusted", "Ignore security alerts", "Use default passwords", 0, "Assume breach means limiting access by segmenting networks and applying end-to-end encryption.", QuestionDifficulty.MEDIUM),
                ("zero-trust-model", "Azure Active Directory Conditional Access is part of which Zero Trust pillar?", "Identity", "Network", "Data", "Devices", 0, "Conditional Access is a key component of the identity pillar in Zero Trust, controlling access based on conditions.", QuestionDifficulty.HARD),

                # Defense in Depth
                ("defense-in-depth", "What is defense in depth?", "Multiple layers of security controls", "A single strong firewall", "Using only encryption", "Trusting the perimeter", 0, "Defense in depth uses multiple layers of security, so if one fails, others still protect the system.", QuestionDifficulty.EASY),
                ("defense-in-depth", "Which layer of defense in depth protects physical data centers?", "Physical security", "Perimeter security", "Network security", "Application security", 0, "Physical security is the outermost layer, protecting data centers from unauthorized physical access.", QuestionDifficulty.EASY),
                ("defense-in-depth", "Which security layer protects data at rest and in transit?", "Data security", "Perimeter security", "Identity security", "Host security", 0, "Data security includes encryption of data at rest and in transit, plus data classification and loss prevention.", QuestionDifficulty.MEDIUM),
                ("defense-in-depth", "Network security groups provide protection at which layer?", "Network security layer", "Application layer", "Data layer", "Physical layer", 0, "NSGs filter traffic at the network layer by defining allow/deny rules for network traffic.", QuestionDifficulty.MEDIUM),
                ("defense-in-depth", "What does the identity layer of defense in depth include?", "Multi-factor authentication, conditional access, and role-based access control", "Firewalls and network segmentation", "Data encryption", "Physical locks", 0, "The identity layer includes MFA, conditional access, RBAC, and identity governance.", QuestionDifficulty.HARD),

                # Defender for Cloud
                ("defender-for-cloud", "What is Microsoft Defender for Cloud?", "A cloud security posture management and workload protection tool", "A firewall service", "A VPN gateway", "A monitoring tool only", 0, "Defender for Cloud provides CSPM and workload protection across hybrid cloud workloads.", QuestionDifficulty.MEDIUM),
                ("defender-for-cloud", "What does the free tier of Defender for Cloud provide?", "Security posture management for Azure resources", "Full workload protection", "DDoS protection", "VPN management", 0, "The free tier provides basic security posture management and recommendations for Azure resources.", QuestionDifficulty.MEDIUM),
                ("defender-for-cloud", "What is a Secure Score in Defender for Cloud?", "A numerical indicator of security posture", "A password strength meter", "A network speed test", "A cost estimate", 0, "Secure Score is a measurement of an organization's security posture, with recommendations for improvement.", QuestionDifficulty.MEDIUM),
                ("defender-for-cloud", "Defender for Cloud can protect which types of workloads?", "Azure, on-premises, and other cloud providers", "Only Azure VMs", "Only web applications", "Only databases", 0, "Defender for Cloud provides protection for Azure, on-premises, and multi-cloud workloads.", QuestionDifficulty.HARD),
                ("defender-for-cloud", "What does CSPM stand for in Defender for Cloud?", "Cloud Security Posture Management", "Cloud Service Provider Management", "Central Security Policy Manager", "Cloud System Performance Monitor", 0, "CSPM continuously assesses your cloud environment for security vulnerabilities and compliance.", QuestionDifficulty.EASY),

                # Key Vault
                ("azure-key-vault", "What is Azure Key Vault used for?", "Storing and managing secrets, keys, and certificates", "Storing database backups", "Managing virtual machines", "Hosting web applications", 0, "Key Vault provides secure storage for secrets, encryption keys, and certificates.", QuestionDifficulty.EASY),
                ("azure-key-vault", "Which type of Key Vault stores cryptographic keys and secrets?", "Key Vault (Standard or Premium)", "Blob Storage", "Cosmos DB", "Table Storage", 0, "Key Vault Standard stores secrets and keys, while Premium adds HSM-backed keys.", QuestionDifficulty.MEDIUM),
                ("azure-key-vault", "What is the benefit of using Key Vault for secrets management?", "Centralized secrets management with access control and audit logging", "Faster database queries", "Better network performance", "Cheaper storage costs", 0, "Key Vault provides centralized secret management with RBAC integration and detailed audit logs.", QuestionDifficulty.MEDIUM),
                ("azure-key-vault", "What is Managed HSM in Azure Key Vault?", "A fully managed single-tenant HSM service", "A software-based encryption tool", "A network security feature", "A backup service", 0, "Managed HSM provides a dedicated, single-tenant HSM for cryptographic key management.", QuestionDifficulty.HARD),
                ("azure-key-vault", "Key Vault access can be controlled through:", "Azure RBAC and access policies", "Only username and password", "IP address whitelisting only", "Physical key cards", 0, "Key Vault supports both RBAC and access policies for fine-grained access control.", QuestionDifficulty.MEDIUM),

                # Network Security
                ("network-security", "What is the purpose of Azure Firewall?", "Filtering network traffic between Azure and the internet", "Encrypting data at rest", "Managing user identities", "Storing secrets", 0, "Azure Firewall is a managed, cloud-based network security service that protects Azure resources.", QuestionDifficulty.EASY),
                ("network-security", "What does DDoS Protection Standard provide?", "Advanced DDoS mitigation for Azure resources", "Basic network monitoring only", "VPN connectivity", "Storage encryption", 0, "DDoS Protection Standard provides enhanced mitigation against sophisticated DDoS attacks.", QuestionDifficulty.MEDIUM),
                ("network-security", "Azure Web Application Firewall (WAF) protects against:", "Common web exploits and vulnerabilities", "Physical data center intrusions", "Power outages", "Network latency", 0, "WAF protects web applications from common attacks like SQL injection and cross-site scripting.", QuestionDifficulty.MEDIUM),
                ("network-security", "Which Azure service provides private connectivity between Azure and on-premises?", "VPN Gateway or ExpressRoute", "Azure Firewall", "Azure Front Door", "Azure CDN", 0, "VPN Gateway and ExpressRoute provide secure connectivity between on-premises and Azure networks.", QuestionDifficulty.MEDIUM),
                ("network-security", "What is the principle of least privilege in network security?", "Granting only the minimum network access needed", "Allowing all traffic", "Blocking all inbound traffic", "Using only public IPs", 0, "Least privilege network security means only allowing necessary traffic through NSGs and firewalls.", QuestionDifficulty.MEDIUM),
            ]

            # Insert questions
            for q_data in questions_data:
                topic_slug, q_text, opt_a, opt_b, opt_c, opt_d, correct_idx, explanation, difficulty = q_data
                topic_id = topics_map.get(topic_slug)
                if not topic_id:
                    continue

                # Determine domain
                topic = db.query(Topic).filter(Topic.id == topic_id).first()
                if not topic:
                    continue

                q = Question(
                    exam_version_id=ev.id,
                    domain_id=topic.domain_id,
                    topic_id=topic_id,
                    question_text=q_text,
                    question_type=QuestionType.SINGLE_CHOICE,
                    difficulty=difficulty,
                    access_level=AccessLevel.FREE,
                    explanation=explanation,
                    source_type="original",
                )
                db.add(q)
                db.flush()

                options = [opt_a, opt_b, opt_c, opt_d]
                for i, opt_text in enumerate(options):
                    o = QuestionOption(
                        question_id=q.id,
                        option_text=opt_text,
                        is_correct=(i == correct_idx),
                    )
                    db.add(o)

            # --- Premium Questions (5 per topic sample) ---
            premium_questions_data = [
                ("what-is-cloud-computing", "A company wants to deploy an application that requires Windows Server, IIS, and .NET. They want to minimize management overhead. Which Azure compute option is best?", "Azure App Service (PaaS)", "Azure Virtual Machines (IaaS)", "Azure Functions", "Azure Container Instances", 0, "Azure App Service is PaaS, meaning Microsoft manages the OS, IIS, and runtime, minimizing management overhead while supporting Windows web apps.", QuestionDifficulty.HARD),
                ("what-is-cloud-computing", "Which statement about the difference between IaaS and PaaS is correct?", "PaaS includes OS management by the provider; IaaS does not", "IaaS includes OS management by the provider", "PaaS requires the customer to manage hardware", "IaaS is always more expensive than PaaS", 0, "In PaaS, the provider manages the OS and runtime. In IaaS, the customer manages the OS.", QuestionDifficulty.HARD),
                ("what-is-cloud-computing", "A financial company must keep all data within EU borders due to GDPR. Which Azure feature addresses this?", "Data residency policies with Azure regions", "Azure Cost Management", "Azure DevOps", "Azure Front Door", 0, "Azure data residency policies allow organizations to select regions where data will be stored, ensuring compliance with regulations like GDPR.", QuestionDifficulty.HARD),
                ("what-is-cloud-computing", "An organization wants to migrate 500 VMs to Azure. They need to minimize costs for predictable, steady-state workloads. What should they use?", "Azure Reserved Virtual Machine Instances", "Pay-as-you-go pricing", "Spot VMs only", "Azure Dev/Test pricing", 0, "Reserved VM Instances offer up to 72% savings for predictable, steady-state workloads compared to pay-as-you-go.", QuestionDifficulty.HARD),
                ("what-is-cloud-computing", "What is the maximum number of virtual CPUs that can be assigned to a single Azure Virtual Machine?", "It depends on the VM size and series", "128 vCPUs always", "64 vCPUs maximum", "256 vCPUs maximum", 0, "The number of vCPUs depends on the VM series and size. Some series offer up to 416 vCPUs (Mv2 series).", QuestionDifficulty.HARD),

                ("azure-compute", "Which Azure service should you use to run a batch processing job that runs once a month for 10 minutes?", "Azure Functions", "Azure Virtual Machines", "Azure App Service", "Azure Kubernetes Service", 0, "Azure Functions is ideal for event-driven, short-running tasks that run on-demand without provisioning servers.", QuestionDifficulty.HARD),
                ("azure-compute", "You need to run a Linux container workload that requires orchestration. Which service?", "Azure Kubernetes Service (AKS)", "Azure Container Instances", "Azure Virtual Machines", "Azure App Service", 0, "AKS provides a managed Kubernetes environment for orchestrating containerized applications at scale.", QuestionDifficulty.HARD),
                ("azure-compute", "A company needs to run a legacy application that requires a specific Windows Server version. Which service?", "Azure Virtual Machines", "Azure App Service", "Azure Functions", "Azure Container Instances", 0, "Azure VMs allow you to choose the exact OS version needed for legacy applications.", QuestionDifficulty.MEDIUM),
                ("azure-compute", "What is the difference between Azure VMs and Azure Virtual Machine Scale Sets?", "Scale Sets auto-scale VMs based on demand; VMs are single instances", "No difference", "Scale Sets are for containers only", "VMs auto-scale automatically", 0, "VM Scale Sets automatically increase or decrease VM instances based on demand or schedule.", QuestionDifficulty.HARD),
                ("azure-compute", "Which Azure service provides GPU-enabled VMs for machine learning workloads?", "Azure GPU VMs (NC, ND series)", "Azure Functions", "Azure App Service", "Azure Container Instances", 0, "NC and ND series VMs provide GPU capabilities for compute-intensive workloads like ML training.", QuestionDifficulty.HARD),

                ("azure-networking", "A company needs to connect two VNets in different Azure regions. Which service should they use?", "VNet Peering", "Azure Load Balancer", "Azure DNS", "Network Security Group", 0, "VNet Peering connects two virtual networks, enabling resources to communicate across regions.", QuestionDifficulty.HARD),
                ("azure-networking", "What is the difference between Azure Load Balancer and Azure Application Gateway?", "Load Balancer operates at Layer 4; Application Gateway at Layer 7", "Both operate at the same layer", "Load Balancer is for web apps only", "Application Gateway is cheaper", 0, "Load Balancer works at TCP/UDP level (L4), while Application Gateway provides HTTP/HTTPS routing (L7) with WAF.", QuestionDifficulty.HARD),
                ("azure-networking", "You need to route traffic to the closest Azure region based on user location. Which service?", "Azure Traffic Manager", "Azure Load Balancer", "Azure DNS", "Azure Firewall", 0, "Traffic Manager uses DNS-based routing to direct traffic to the closest endpoint based on user location.", QuestionDifficulty.HARD),
                ("azure-networking", "What is the purpose of Azure Bastion?", "Secure RDP/SSH access to VMs without exposing public IPs", "Load balancing web traffic", "Managing DNS records", "Storing encryption keys", 0, "Azure Bastion provides secure RDP/SSH access to VMs directly in the Azure portal without public IP exposure.", QuestionDifficulty.HARD),
                ("azure-networking", "Which protocol does Azure ExpressRoute use to connect on-premises to Azure?", "Private, dedicated network connection via a connectivity provider", "VPN over the internet", "Public internet connection", "Satellite link", 0, "ExpressRoute provides a private, dedicated connection through a connectivity provider, not over the public internet.", QuestionDifficulty.HARD),

                ("azure-storage", "You need to store 500 TB of backup data that will be accessed once a year. Which access tier?", "Archive tier", "Hot tier", "Cool tier", "Premium tier", 0, "Archive tier is the most cost-effective for data that is rarely accessed, with retrieval taking hours.", QuestionDifficulty.HARD),
                ("azure-storage", "A web application needs to serve static content globally with low latency. Which Azure service?", "Azure CDN with Blob Storage", "Azure Queue Storage", "Azure Table Storage", "Azure File Storage", 0, "Azure CDN caches Blob Storage content at edge locations worldwide for low-latency access.", QuestionDifficulty.HARD),
                ("azure-storage", "What is Azure Data Lake Storage Gen2?", "A storage service optimized for big data analytics workloads", "A backup service", "A database service", "A messaging service", 0, "ADLS Gen2 combines the capabilities of Azure Data Lake Storage with Azure Blob Storage for analytics.", QuestionDifficulty.HARD),
                ("azure-storage", "Which redundancy option copies data to a secondary region asynchronously?", "Geo-redundant storage (GRS)", "Locally redundant storage (LRS)", "Zone-redundant storage (ZRS)", "Read-access geo-redundant storage (RA-GRS)", 0, "GRS asynchronously replicates data to a secondary region hundreds of miles away for disaster recovery.", QuestionDifficulty.HARD),
                ("azure-storage", "What is the difference between Block Blobs and Append Blobs?", "Append Blobs support append operations; Block Blobs support block operations", "No difference", "Append Blobs are faster", "Block Blobs are for databases only", 0, "Block Blobs are for text/binary data with block-level management. Append Blobs are optimized for append operations like logging.", QuestionDifficulty.HARD),

                ("cost-management", "A company runs dev/test workloads. How can they reduce costs?", "Use Azure Dev/Test subscriptions with special pricing", "Use only production VMs", "Deploy to multiple regions", "Use Premium storage only", 0, "Azure Dev/Test subscriptions provide discounted rates for development and testing scenarios.", QuestionDifficulty.HARD),
                ("cost-management", "What is the Azure Hybrid Benefit?", "Apply existing on-premises licenses to Azure to reduce costs", "Free Azure credits for new users", "A discount for annual payments", "A VPN service", 0, "Azure Hybrid Benefit allows you to use existing Windows Server and SQL Server licenses on Azure for savings.", QuestionDifficulty.HARD),
                ("cost-management", "Which tool provides the most detailed cost breakdown by resource tag?", "Azure Cost Management", "Azure Monitor", "Azure Advisor", "Azure Portal home page", 0, "Azure Cost Management allows filtering and grouping costs by resource tags for detailed analysis.", QuestionDifficulty.HARD),
                ("cost-management", "You want to set a budget and get alerts when spending exceeds a threshold. Which service?", "Azure Cost Management budgets", "Azure Monitor alerts", "Azure Policy", "Azure Advisor", 0, "Azure Cost Management allows setting budgets with alert rules when actual or forecasted costs exceed thresholds.", QuestionDifficulty.MEDIUM),
                ("cost-management", "What is the difference between Azure Dev/Test pricing and Reserved Instances?", "Dev/Test is for development workloads; Reserved Instances are for production with commitment", "They are the same thing", "Dev/Test is for production only", "Reserved Instances are free", 0, "Dev/Test provides discounted rates for non-production workloads, while Reserved Instances offer savings for committed production workloads.", QuestionDifficulty.HARD),
            ]

            for q_data in premium_questions_data:
                topic_slug, q_text, opt_a, opt_b, opt_c, opt_d, correct_idx, explanation, difficulty = q_data
                topic_id = topics_map.get(topic_slug)
                if not topic_id:
                    continue
                topic = db.query(Topic).filter(Topic.id == topic_id).first()
                if not topic:
                    continue

                q = Question(
                    exam_version_id=ev.id,
                    domain_id=topic.domain_id,
                    topic_id=topic_id,
                    question_text=q_text,
                    question_type=QuestionType.SINGLE_CHOICE,
                    difficulty=difficulty,
                    access_level=AccessLevel.PREMIUM,
                    explanation=explanation,
                    source_type="original-premium",
                )
                db.add(q)
                db.flush()

                options = [opt_a, opt_b, opt_c, opt_d]
                for i, opt_text in enumerate(options):
                    o = QuestionOption(
                        question_id=q.id,
                        option_text=opt_text,
                        is_correct=(i == correct_idx),
                    )
                    db.add(o)

            # --- Learning Resources ---
            lr_data = [
                ("what-is-cloud-computing", "Microsoft Learn: Cloud Computing Concepts", "Official Microsoft documentation on cloud computing", "https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/", "Microsoft Learn", ResourceType.OFFICIAL_DOCUMENTATION, True),
                ("benefits-of-cloud", "Azure Cloud Benefits Overview", "Overview of Azure cloud benefits", "https://azure.microsoft.com/en-us/overview/what-is-azure/", "Microsoft Azure", ResourceType.OFFICIAL_DOCUMENTATION, True),
                ("cloud-models", "Cloud Deployment Models Explained", "Understanding public, private, and hybrid clouds", "https://learn.microsoft.com/en-us/azure/architecture/cloud-adoption/", "Microsoft Learn", ResourceType.OFFICIAL_DOCUMENTATION, True),
                ("azure-compute", "Azure Compute Documentation", "Complete guide to Azure compute services", "https://learn.microsoft.com/en-us/azure/", "Microsoft Learn", ResourceType.OFFICIAL_DOCUMENTATION, True),
                ("azure-networking", "Azure Networking Documentation", "Azure networking services overview", "https://learn.microsoft.com/en-us/azure/networking/", "Microsoft Learn", ResourceType.OFFICIAL_DOCUMENTATION, True),
                ("azure-storage", "Azure Storage Documentation", "Azure storage services overview", "https://learn.microsoft.com/en-us/azure/storage/", "Microsoft Learn", ResourceType.OFFICIAL_DOCUMENTATION, True),
                ("azure-databases", "Azure Database Services", "Overview of Azure database offerings", "https://learn.microsoft.com/en-us/azure/azure-sql/", "Microsoft Learn", ResourceType.OFFICIAL_DOCUMENTATION, True),
                ("cost-management", "Azure Cost Management", "Managing and optimizing Azure costs", "https://learn.microsoft.com/en-us/azure/cost-management/", "Microsoft Learn", ResourceType.OFFICIAL_DOCUMENTATION, True),
                ("azure-key-vault", "Azure Key Vault Documentation", "Secrets and key management in Azure", "https://learn.microsoft.com/en-us/azure/key-vault/", "Microsoft Learn", ResourceType.OFFICIAL_DOCUMENTATION, True),
            ]

            for concept_slug, title, desc, url, source, rtype, is_official in lr_data:
                concept_id = concepts_map.get(concept_slug)
                if concept_id:
                    lr = LearningResource(
                        concept_id=concept_id,
                        title=title,
                        description=desc,
                        url=url,
                        source=source,
                        resource_type=rtype,
                        is_official=is_official,
                    )
                    db.add(lr)

            # --- Flashcards ---
            flashcard_data = [
                ("what-is-cloud-computing", "What is cloud computing?", "Delivery of computing services (servers, storage, databases, networking, software) over the internet."),
                ("what-is-cloud-computing", "What are the 5 characteristics of cloud computing?", "On-demand self-service, Broad network access, Resource pooling, Rapid elasticity, Measured service."),
                ("benefits-of-cloud", "What are the main benefits of cloud computing?", "Scalability, Cost efficiency, Reliability, Global reach, Speed, Security."),
                ("benefits-of-cloud", "What is CapEx vs OpEx?", "CapEx = Capital Expenditure (buying assets upfront). OpEx = Operational Expenditure (pay-as-you-go)."),
                ("cloud-models", "What are the 3 cloud deployment models?", "Public cloud, Private cloud, Hybrid cloud."),
                ("shared-responsibility-model", "Who manages physical security in all cloud models?", "The cloud provider is always responsible for physical data center security."),
                ("azure-compute", "What is Azure App Service?", "A fully managed PaaS for hosting web apps, REST APIs, and mobile backends."),
                ("azure-compute", "What is Azure Functions?", "Serverless compute service that runs code in response to events without managing servers."),
                ("azure-networking", "What is a VNet?", "A logically isolated section of the Azure network for deploying Azure resources."),
                ("azure-storage", "What are the 3 Blob access tiers?", "Hot (frequent access), Cool (infrequent), Archive (rarely accessed)."),
                ("azure-databases", "What is Azure Cosmos DB?", "A globally distributed, multi-model database service with single-digit millisecond latency."),
                ("zero-trust-model", "What is the core Zero Trust principle?", "Never trust, always verify. Assume breach and verify explicitly."),
                ("defense-in-depth", "What is defense in depth?", "Multiple layers of security controls so if one fails, others still protect the system."),
                ("azure-key-vault", "What is Azure Key Vault used for?", "Storing and managing secrets, encryption keys, and certificates securely."),
                ("cost-management", "What is Azure Reserved Instances?", "Pre-purchased compute capacity for 1-3 years at significant discounts."),
            ]

            for concept_slug, front, back in flashcard_data:
                concept_id = concepts_map.get(concept_slug)
                if concept_id:
                    fc = Flashcard(
                        concept_id=concept_id,
                        front=front,
                        back=back,
                    )
                    db.add(fc)

        # ============================================================
        # AWS Cloud Practitioner
        # ============================================================
        aws = db.query(Certification).filter(Certification.slug == "aws-cloud-practitioner").first()
        if not aws:
            aws = Certification(
                provider_id=providers["aws"].id,
                name="AWS Cloud Practitioner",
                slug="aws-cloud-practitioner",
                code="CLF-C02",
                description="Validate your cloud knowledge with the AWS Cloud Practitioner certification.",
                level="beginner",
                category="cloud",
                estimated_hours=25,
            )
            db.add(aws)
            db.flush()

            ev_aws = ExamVersion(certification_id=aws.id, version="2026", effective_date=datetime(2025, 1, 1), status=ExamVersionStatus.ACTIVE)
            db.add(ev_aws)
            db.flush()

            Product(name="AWS Cloud Practitioner Premium", slug="aws-cp-premium", certification_id=aws.id, price=499.0, currency="INR", product_type=ProductType.CERTIFICATION)
            db.flush()

            aws_domains = [
                ("Cloud Concepts", "Value proposition of AWS", 24, 1),
                ("Security and Compliance", "AWS shared responsibility and security", 30, 2),
                ("Cloud Technology and Services", "AWS compute, storage, database services", 34, 3),
                ("Pricing, Billing, and Support", "AWS pricing models and support plans", 12, 4),
            ]
            aws_topic_slugs = {}
            for d_name, d_desc, d_weight, d_order in aws_domains:
                d = Domain(exam_version_id=ev_aws.id, name=d_name, description=d_desc, weight_percentage=d_weight, order_index=d_order)
                db.add(d)
                db.flush()

            # Add AWS topics and questions as needed
            aws_t1 = Topic(domain_id=d.id, name="Cloud Value Proposition", slug="cloud-value-proposition", description="Benefits of cloud", order_index=1)
            db.add(aws_t1)
            db.flush()

            # Sample questions
            for q_text, opt_a, opt_b, opt_c, opt_d, correct, explanation in [
                ("What is the AWS shared responsibility model?", "Customer and AWS share security responsibilities", "AWS manages everything", "Customer manages everything", "No shared model exists", 0, "AWS handles security OF the cloud; customer handles security IN the cloud."),
                ("Which AWS service provides on-demand compute capacity?", "Amazon EC2", "Amazon S3", "Amazon RDS", "Amazon DynamoDB", 0, "EC2 provides resizable compute capacity in the cloud."),
                ("What does 'elasticity' mean in AWS?", "Ability to scale resources up or down automatically", "Fixed resource allocation", "Manual server management", "Physical hardware upgrades", 0, "Elasticity is the ability to automatically adjust resources based on demand."),
                ("Which AWS service is best for object storage?", "Amazon S3", "Amazon EBS", "Amazon EFS", "Amazon Glacier", 0, "S3 is AWS's object storage service for storing and retrieving any amount of data."),
                ("What is the pay-as-you-go model in AWS?", "You only pay for the resources you actually use", "You pay a fixed monthly fee", "You pay upfront for all resources", "You get free resources only", 0, "Pay-as-you-go means you're charged only for the compute time and resources consumed."),
            ]:
                q = Question(
                    exam_version_id=ev_aws.id, domain_id=d.id, topic_id=aws_t1.id,
                    question_text=q_text, question_type=QuestionType.SINGLE_CHOICE,
                    difficulty=QuestionDifficulty.MEDIUM, access_level=AccessLevel.FREE,
                    explanation=explanation, source_type="original",
                )
                db.add(q)
                db.flush()
                for i, opt in enumerate([opt_a, opt_b, opt_c, opt_d]):
                    db.add(QuestionOption(question_id=q.id, option_text=opt, is_correct=(i == correct)))

        # ============================================================
        # Cisco CCNA
        # ============================================================
        ccna = db.query(Certification).filter(Certification.slug == "ccna").first()
        if not ccna:
            ccna = Certification(
                provider_id=providers["cisco"].id,
                name="CCNA 200-301",
                slug="ccna",
                code="200-301",
                description="Validate your ability to install, configure, and troubleshoot networks.",
                level="associate",
                category="networking",
                estimated_hours=40,
            )
            db.add(ccna)
            db.flush()

            ev_ccna = ExamVersion(certification_id=ccna.id, version="2026", effective_date=datetime(2025, 1, 1), status=ExamVersionStatus.ACTIVE)
            db.add(ev_ccna)
            db.flush()

            Product(name="CCNA Premium", slug="ccna-premium", certification_id=ccna.id, price=699.0, currency="INR", product_type=ProductType.CERTIFICATION)
            db.flush()

            ccna_d = Domain(exam_version_id=ev_ccna.id, name="Network Fundamentals", description="OSI model, TCP/IP, IP addressing", weight_percentage=20, order_index=1)
            db.add(ccna_d)
            db.flush()

            ccna_t = Topic(domain_id=ccna_d.id, name="OSI Model", slug="osi-model", description="The 7-layer OSI model", order_index=1)
            db.add(ccna_t)
            db.flush()

            for q_text, opt_a, opt_b, opt_c, opt_d, correct, explanation in [
                ("How many layers does the OSI model have?", "7", "4", "5", "6", 0, "The OSI model has 7 layers: Physical, Data Link, Network, Transport, Session, Presentation, Application."),
                ("Which OSI layer is responsible for routing?", "Network layer (Layer 3)", "Data Link layer (Layer 2)", "Transport layer (Layer 4)", "Physical layer (Layer 1)", 0, "The Network layer handles routing and IP addressing."),
                ("What protocol operates at Layer 4 of the OSI model?", "TCP/UDP", "IP", "Ethernet", "HTTP", 0, "TCP and UDP operate at the Transport layer (Layer 4)."),
                ("What is the purpose of ARP?", "Map IP addresses to MAC addresses", "Map MAC addresses to IP addresses", "Route packets between networks", "Encrypt data in transit", 0, "ARP resolves IP addresses to MAC addresses on a local network."),
                ("What is a subnet mask used for?", "Dividing an IP address into network and host portions", "Encrypting network traffic", "Assigning IP addresses automatically", "Filtering network traffic", 0, "A subnet mask determines which part of an IP address is the network ID vs host ID."),
            ]:
                q = Question(
                    exam_version_id=ev_ccna.id, domain_id=ccna_d.id, topic_id=ccna_t.id,
                    question_text=q_text, question_type=QuestionType.SINGLE_CHOICE,
                    difficulty=QuestionDifficulty.MEDIUM, access_level=AccessLevel.FREE,
                    explanation=explanation, source_type="original",
                )
                db.add(q)
                db.flush()
                for i, opt in enumerate([opt_a, opt_b, opt_c, opt_d]):
                    db.add(QuestionOption(question_id=q.id, option_text=opt, is_correct=(i == correct)))

        # ============================================================
        # CompTIA Security+
        # ============================================================
        secplus = db.query(Certification).filter(Certification.slug == "security-plus").first()
        if not secplus:
            secplus = Certification(
                provider_id=providers["comptia"].id,
                name="CompTIA Security+",
                slug="security-plus",
                code="SY0-701",
                description="Validate baseline cybersecurity skills.",
                level="associate",
                category="security",
                estimated_hours=35,
            )
            db.add(secplus)
            db.flush()

            ev_sec = ExamVersion(certification_id=secplus.id, version="2026", effective_date=datetime(2025, 1, 1), status=ExamVersionStatus.ACTIVE)
            db.add(ev_sec)
            db.flush()

            Product(name="Security+ Premium", slug="security-plus-premium", certification_id=secplus.id, price=699.0, currency="INR", product_type=ProductType.CERTIFICATION)
            db.flush()

            sec_d = Domain(exam_version_id=ev_sec.id, name="General Security Concepts", description="Security controls and concepts", weight_percentage=12, order_index=1)
            db.add(sec_d)
            db.flush()

            sec_t = Topic(domain_id=sec_d.id, name="Security Controls", slug="security-controls", description="Types of security controls", order_index=1)
            db.add(sec_t)
            db.flush()

            for q_text, opt_a, opt_b, opt_c, opt_d, correct, explanation in [
                ("What are the four categories of security controls?", "Technical, Managerial, Operational, Physical", "Hardware, Software, Network, Data", "Input, Output, Processing, Storage", "Authentication, Authorization, Accounting, Auditing", 0, "Security controls are classified into Technical, Managerial, Operational, and Physical categories."),
                ("What is the principle of least privilege?", "Granting only the minimum access needed to perform a function", "Granting full access to all users", "Restricting all network access", "Using multi-factor authentication", 0, "Least privilege ensures users have only the access necessary for their role, reducing attack surface."),
                ("What is a security baseline?", "A minimum set of security configurations for systems", "The maximum security level", "A firewall configuration", "An encryption standard", 0, "A security baseline defines the minimum security settings and configurations for systems."),
                ("What is defense in depth?", "Multiple layers of security controls", "A single strong firewall", "Using only encryption", "Physical security only", 0, "Defense in depth uses multiple overlapping security layers to protect against attacks."),
                ("What is a zero-day vulnerability?", "A vulnerability unknown to the vendor", "A fixed vulnerability", "A known vulnerability", "A physical security flaw", 0, "Zero-day vulnerabilities are unknown to the vendor and have no available patches."),
            ]:
                q = Question(
                    exam_version_id=ev_sec.id, domain_id=sec_d.id, topic_id=sec_t.id,
                    question_text=q_text, question_type=QuestionType.SINGLE_CHOICE,
                    difficulty=QuestionDifficulty.MEDIUM, access_level=AccessLevel.FREE,
                    explanation=explanation, source_type="original",
                )
                db.add(q)
                db.flush()
                for i, opt in enumerate([opt_a, opt_b, opt_c, opt_d]):
                    db.add(QuestionOption(question_id=q.id, option_text=opt, is_correct=(i == correct)))

        # ============================================================
        # Career Paths
        # ============================================================
        career_data = [
            ("Cloud Engineer", "cloud-engineer", "Design, implement, and manage cloud infrastructure on Azure, AWS, or hybrid environments.", "intermediate", 12, "Cloud Computing, Virtual Networking, Storage, Identity Management, ARM Templates")
            ("Cloud Security Engineer", "cloud-security-engineer", "Secure cloud environments, implement zero trust, and manage compliance across cloud platforms.", "advanced", 18, "Zero Trust, Network Security, Identity & Access, Encryption, Compliance, Incident Response")
            ("Cybersecurity Analyst", "cybersecurity-analyst", "Monitor, detect, and respond to cybersecurity threats and vulnerabilities.", "intermediate", 15, "Threat Detection, SIEM, Network Security, Vulnerability Management, Incident Response")
            ("Network Engineer", "network-engineer", "Design, implement, and manage enterprise network infrastructure.", "intermediate", 14, "TCP/IP, Routing, Switching, DNS, VPN, Network Security, Wireless")
            ("DevOps Engineer", "devops-engineer", "Bridge development and operations with CI/CD, automation, and cloud-native practices.", "intermediate", 16, "CI/CD, Containers, Kubernetes, Infrastructure as Code, Monitoring, Cloud Services")
            ("Cloud Developer", "cloud-developer", "Build cloud-native applications using modern architectures and serverless patterns.", "intermediate", 14, "Cloud Services, APIs, Serverless, Containers, Databases, Security")
            ("AI/ML Engineer", "ai-ml-engineer", "Design and implement AI and machine learning solutions on cloud platforms.", "advanced", 20, "Machine Learning, Data Science, Cloud AI Services, MLOps, Statistics")
            ("Systems Administrator", "systems-administrator", "Manage and maintain operating systems, servers, and enterprise infrastructure.", "beginner", 10, "Linux, Windows Server, Networking, Security, Virtualization, Troubleshooting")
        ]

        career_paths = {}
        for c_name, c_slug, c_desc, c_diff, c_months, c_skills in career_data:
            cp = CareerPath(
                name=c_name, slug=c_slug, description=c_desc,
                difficulty=c_diff, estimated_months=c_months,
                skills_covered=c_skills,
            )
            db.add(cp)
            db.flush()
            career_paths[c_slug] = cp

        # Link certifications to career paths
        cert_links = [
            ("cloud-engineer", "az-900", "foundation", 1, True),
            ("cloud-engineer", "aws-cloud-practitioner", "foundation", 2, False),
            ("cloud-security-engineer", "az-900", "foundation", 1, True),
            ("cloud-security-engineer", "security-plus", "intermediate", 2, True),
            ("cybersecurity-analyst", "security-plus", "foundation", 1, True),
            ("network-engineer", "ccna", "foundation", 1, True),
            ("devops-engineer", "az-900", "foundation", 1, False),
            ("cloud-developer", "az-900", "foundation", 1, False),
            ("systems-administrator", "az-900", "foundation", 1, False),
            ("systems-administrator", "security-plus", "intermediate", 2, False),
        ]

        for c_slug, cert_code, stage, order, required in cert_links:
            cp = career_paths.get(c_slug)
            cert = db.query(Certification).filter(Certification.code == cert_code).first()
            if cp and cert:
                cc = CareerCertification(
                    career_path_id=cp.id,
                    certification_id=cert.id,
                    stage=stage,
                    order_index=order,
                    required=required,
                )
                db.add(cc)

        # ============================================================
        # Achievements
        # ============================================================
        achievements_data = [
            ("First Steps", "first-quiz", "Complete your first quiz", "🎯", "quiz", "quizzes_completed", 1, 10),
            ("Question Master", "100-questions", "Answer 100 questions", "📚", "milestone", "questions_answered", 100, 50),
            ("Half Thousand", "500-questions", "Answer 500 questions", "💪", "milestone", "questions_answered", 500, 100),
            ("Quiz Champion", "perfect-quiz", "Score 100% on a quiz", "⭐", "quiz", "perfect_quizzes", 1, 50),
            ("Mock Exam Taker", "first-mock", "Complete your first mock exam", "📝", "mock", "mock_exams", 1, 100),
            ("Streak Warrior", "7-day-streak", "Maintain a 7-day study streak", "🔥", "streak", "streak_days", 7, 100),
            ("Unstoppable", "30-day-streak", "Maintain a 30-day study streak", "🏆", "streak", "streak_days", 30, 500),
            ("Knowledge Seeker", "first-correct", "Get your first correct answer", "✅", "quiz", "correct_answers", 1, 5),
            ("Century Club", "100-correct", "Get 100 correct answers", "💯", "milestone", "correct_answers", 100, 75),
        ]

        for a_name, a_slug, a_desc, a_icon, a_cat, a_req_type, a_req_val, a_xp in achievements_data:
            ach = Achievement(
                name=a_name, slug=a_slug, description=a_desc,
                icon=a_icon, category=a_cat,
                requirement_type=a_req_type, requirement_value=a_req_val,
                xp_reward=a_xp,
            )
            db.add(ach)

        # ============================================================
        # Content Versions
        # ============================================================
        for cert in [az900, aws, ccna, secplus]:
            if cert:
                cv = ContentVersion(
                    certification_id=cert.id,
                    version="2026",
                    content_status="current",
                    last_updated=datetime(2025, 1, 1),
                    changes_summary="Initial content release",
                )
                db.add(cv)

        # ============================================================
        # Demo user gamification
        # ============================================================
        demo_game = UserGamification(user_id=demo.id, total_xp=50, level=1, title="Newcomer")
        db.add(demo_game)

        db.commit()
        print("Seed data created successfully!")
        print(f"  - Admin: admin@niksmind.com / admin123")
        print(f"  - Demo:  demo@niksmind.com / demo123")
        print(f"  - Career paths: {len(career_data)}")
        print(f"  - Achievements: {len(achievements_data)}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
