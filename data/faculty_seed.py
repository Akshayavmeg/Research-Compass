"""
data/faculty_seed.py
=====================
Source-of-truth seed data for 16 realistic faculty profiles, covering
every research area requested by the project brief. This module is
imported by utils/ingest.py to (a) materialize one .txt document per
faculty member under data/faculty/ and (b) load them into ChromaDB.

Editing this list and re-running `python scripts/init_chroma.py` is the
supported way to add/update faculty.
"""

FACULTY_SEED = [
    {
        "id": "fac_001",
        "name": "Dr. Ananya Rao",
        "designation": "Associate Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Natural Language Processing", "Large Language Models", "Information Retrieval"],
        "keywords": ["transformers", "LLMs", "text summarization", "question answering", "RAG"],
        "current_projects": [
            "Domain-adaptive fine-tuning for low-resource Indian languages",
            "Retrieval-augmented generation for legal document search",
        ],
        "publications": [
            "Rao, A. et al. (2023) 'Cross-lingual Transfer for Low-Resource NLP', ACL.",
            "Rao, A. & Iyer, S. (2022) 'Efficient RAG Pipelines for Enterprise Search', EMNLP.",
        ],
        "experience_years": 11,
        "max_project_slots": 4,
        "current_project_count": 3,
        "past_students": ["Priya Menon", "Karthik S.", "Fatima Sheikh"],
        "email": "ananya.rao@university.edu",
        "office": "CSE Block A, Room 214",
        "biography": (
            "Dr. Ananya Rao leads the NLP & Language Understanding Lab. Her work focuses on making "
            "large language models practical for low-resource languages and enterprise retrieval "
            "settings. She has supervised 12 graduate theses and holds two patents in text summarization."
        ),
    },
    {
        "id": "fac_002",
        "name": "Dr. Vikram Nair",
        "designation": "Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Computer Vision", "Deep Learning", "Medical Imaging"],
        "keywords": ["CNNs", "object detection", "segmentation", "diffusion models", "vision transformers"],
        "current_projects": [
            "Automated tumor segmentation from MRI scans",
            "Real-time defect detection for manufacturing lines",
        ],
        "publications": [
            "Nair, V. (2023) 'Vision Transformers for Medical Image Segmentation', CVPR.",
            "Nair, V. & Das, R. (2021) 'Lightweight Object Detectors for Edge Devices', ICCV.",
        ],
        "experience_years": 16,
        "max_project_slots": 5,
        "current_project_count": 5,
        "past_students": ["Rohan Verma", "Aisha Khan"],
        "email": "vikram.nair@university.edu",
        "office": "CSE Block B, Room 108",
        "biography": (
            "Dr. Vikram Nair directs the Vision & Perception Lab, with 16 years of experience spanning "
            "academic and industrial computer vision. His current focus is efficient vision transformers "
            "deployable on edge hardware for healthcare and manufacturing."
        ),
    },
    {
        "id": "fac_003",
        "name": "Dr. Meera Iyer",
        "designation": "Assistant Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Machine Learning", "Reinforcement Learning", "Time-Series Forecasting"],
        "keywords": ["RL", "bandits", "forecasting", "causal inference", "AutoML"],
        "current_projects": [
            "Reinforcement learning for adaptive tutoring systems",
            "Causal forecasting for energy demand prediction",
        ],
        "publications": [
            "Iyer, M. (2024) 'Causal Bandits for Adaptive Learning Systems', NeurIPS.",
        ],
        "experience_years": 6,
        "max_project_slots": 3,
        "current_project_count": 1,
        "past_students": ["Devansh Gupta"],
        "email": "meera.iyer@university.edu",
        "office": "CSE Block A, Room 301",
        "biography": (
            "Dr. Meera Iyer joined the department after a postdoc at a leading RL lab. She is especially "
            "interested in applying reinforcement learning to real-world adaptive systems such as "
            "personalized education and energy management."
        ),
    },
    {
        "id": "fac_004",
        "name": "Dr. Suresh Pillai",
        "designation": "Professor",
        "department": "Cyber Security",
        "research_areas": ["Cyber Security", "Network Security", "Applied Cryptography"],
        "keywords": ["intrusion detection", "malware analysis", "zero trust", "cryptography", "penetration testing"],
        "current_projects": [
            "AI-assisted intrusion detection for campus networks",
            "Post-quantum cryptography readiness assessment",
        ],
        "publications": [
            "Pillai, S. (2022) 'Machine Learning for Network Intrusion Detection: A Survey', IEEE S&P.",
        ],
        "experience_years": 19,
        "max_project_slots": 4,
        "current_project_count": 2,
        "past_students": ["Nikhil Rathi", "Sana Fernandes", "Arjun Bose"],
        "email": "suresh.pillai@university.edu",
        "office": "Security Research Building, Room 12",
        "biography": (
            "Dr. Suresh Pillai heads the Cyber Security Research Group and consults for national CERT "
            "initiatives. His lab studies both offensive and defensive security, with a growing focus on "
            "how machine learning changes the threat landscape."
        ),
    },
    {
        "id": "fac_005",
        "name": "Dr. Kavya Reddy",
        "designation": "Associate Professor",
        "department": "Electronics & Communication",
        "research_areas": ["Internet of Things", "Embedded Systems", "Edge Computing"],
        "keywords": ["IoT", "sensor networks", "low-power design", "edge AI", "firmware"],
        "current_projects": [
            "Low-power sensor networks for precision agriculture",
            "Edge AI inference on microcontrollers",
        ],
        "publications": [
            "Reddy, K. (2023) 'TinyML for Agricultural Sensor Networks', IEEE IoT Journal.",
        ],
        "experience_years": 9,
        "max_project_slots": 4,
        "current_project_count": 3,
        "past_students": ["Manish Joshi"],
        "email": "kavya.reddy@university.edu",
        "office": "ECE Building, Room 45",
        "biography": (
            "Dr. Kavya Reddy's lab builds low-power IoT systems deployed in real agricultural fields "
            "across three states. She is particularly interested in TinyML — squeezing useful inference "
            "onto milliwatt-scale hardware."
        ),
    },
    {
        "id": "fac_006",
        "name": "Dr. Arjun Malhotra",
        "designation": "Assistant Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Blockchain", "Distributed Systems", "Cryptoeconomics"],
        "keywords": ["consensus protocols", "smart contracts", "DeFi", "Byzantine fault tolerance", "distributed ledgers"],
        "current_projects": [
            "Scalable consensus protocols for permissioned blockchains",
            "Formal verification of smart contracts",
        ],
        "publications": [
            "Malhotra, A. (2023) 'Byzantine Fault Tolerant Consensus at Scale', ICDCS.",
        ],
        "experience_years": 5,
        "max_project_slots": 3,
        "current_project_count": 3,
        "past_students": [],
        "email": "arjun.malhotra@university.edu",
        "office": "CSE Block C, Room 22",
        "biography": (
            "Dr. Arjun Malhotra studies the intersection of distributed systems and economic incentive "
            "design. Before joining academia he worked on consensus engineering at a blockchain startup."
        ),
    },
    {
        "id": "fac_007",
        "name": "Dr. Priyanka Desai",
        "designation": "Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Cloud Computing", "Distributed Systems", "Systems Performance"],
        "keywords": ["Kubernetes", "microservices", "serverless", "resource scheduling", "container orchestration"],
        "current_projects": [
            "Cost-aware autoscaling for serverless workloads",
            "Energy-efficient scheduling in multi-tenant clusters",
        ],
        "publications": [
            "Desai, P. (2021) 'Cost-Aware Autoscaling in Serverless Platforms', ACM SoCC.",
            "Desai, P. & Nair, V. (2020) 'Energy-Efficient Scheduling for Cloud Clusters', USENIX ATC.",
        ],
        "experience_years": 14,
        "max_project_slots": 4,
        "current_project_count": 2,
        "past_students": ["Rahul Kapoor", "Divya Shah"],
        "email": "priyanka.desai@university.edu",
        "office": "CSE Block B, Room 219",
        "biography": (
            "Dr. Priyanka Desai's Cloud Systems Lab partners with several industry cloud providers to "
            "study real production workloads. She teaches the department's flagship distributed systems "
            "course."
        ),
    },
    {
        "id": "fac_008",
        "name": "Dr. Rohit Chandra",
        "designation": "Associate Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Big Data", "Data Mining", "Data Engineering"],
        "keywords": ["Spark", "data pipelines", "pattern mining", "streaming analytics", "data warehousing"],
        "current_projects": [
            "Real-time anomaly detection over streaming data pipelines",
            "Scalable pattern mining for retail transaction logs",
        ],
        "publications": [
            "Chandra, R. (2022) 'Scalable Streaming Anomaly Detection', IEEE Big Data.",
        ],
        "experience_years": 10,
        "max_project_slots": 3,
        "current_project_count": 3,
        "past_students": ["Yash Trivedi", "Neha Bhat"],
        "email": "rohit.chandra@university.edu",
        "office": "CSE Block A, Room 118",
        "biography": (
            "Dr. Rohit Chandra's research turns messy, high-volume data into reliable real-time signals. "
            "He collaborates closely with retail and logistics industry partners on applied data mining."
        ),
    },
    {
        "id": "fac_009",
        "name": "Dr. Sneha Kulkarni",
        "designation": "Assistant Professor",
        "department": "Electronics & Communication",
        "research_areas": ["Networking", "Wireless Communication", "5G/6G Systems"],
        "keywords": ["5G", "network slicing", "SDN", "wireless protocols", "network optimization"],
        "current_projects": [
            "Dynamic network slicing for 5G private networks",
            "SDN-based traffic engineering for campus backbones",
        ],
        "publications": [
            "Kulkarni, S. (2023) 'Dynamic Network Slicing in 5G Core Networks', IEEE Trans. Networking.",
        ],
        "experience_years": 7,
        "max_project_slots": 3,
        "current_project_count": 1,
        "past_students": ["Om Prakash"],
        "email": "sneha.kulkarni@university.edu",
        "office": "ECE Building, Room 67",
        "biography": (
            "Dr. Sneha Kulkarni's Networking Lab focuses on making next-generation wireless networks "
            "programmable and efficient, with active collaborations with telecom operators."
        ),
    },
    {
        "id": "fac_010",
        "name": "Dr. Anil Bhatt",
        "designation": "Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Distributed Systems", "Fault Tolerance", "Database Systems"],
        "keywords": ["consensus", "replication", "distributed databases", "fault tolerance", "consistency models"],
        "current_projects": [
            "Geo-replicated database consistency under network partitions",
            "Self-healing distributed storage systems",
        ],
        "publications": [
            "Bhatt, A. (2020) 'Consistency Models for Geo-Replicated Databases', VLDB.",
        ],
        "experience_years": 20,
        "max_project_slots": 4,
        "current_project_count": 4,
        "past_students": ["Tanvi Rao", "Girish Kumar", "Alok Nath"],
        "email": "anil.bhatt@university.edu",
        "office": "CSE Block B, Room 305",
        "biography": (
            "Dr. Anil Bhatt is one of the department's most senior faculty, with two decades of work on "
            "distributed databases. Several of his former students now lead systems teams at major tech "
            "companies."
        ),
    },
    {
        "id": "fac_011",
        "name": "Dr. Ritu Sharma",
        "designation": "Associate Professor",
        "department": "Electronics & Communication",
        "research_areas": ["Embedded Systems", "Robotics", "Control Systems"],
        "keywords": ["robotics", "motion planning", "embedded control", "SLAM", "real-time systems"],
        "current_projects": [
            "Autonomous navigation for warehouse robots",
            "Real-time control firmware for robotic arms",
        ],
        "publications": [
            "Sharma, R. (2022) 'SLAM for Low-Cost Warehouse Robots', IEEE ICRA.",
        ],
        "experience_years": 12,
        "max_project_slots": 4,
        "current_project_count": 2,
        "past_students": ["Kabir Singh", "Ishaan Roy"],
        "email": "ritu.sharma@university.edu",
        "office": "Robotics Lab, Room 3",
        "biography": (
            "Dr. Ritu Sharma runs the Robotics & Autonomous Systems Lab, building robots that operate "
            "reliably on constrained embedded hardware in real warehouses."
        ),
    },
    {
        "id": "fac_012",
        "name": "Dr. Deepak Menon",
        "designation": "Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Software Engineering", "Program Analysis", "DevOps"],
        "keywords": ["static analysis", "test generation", "CI/CD", "software quality", "refactoring"],
        "current_projects": [
            "Automated test generation using large language models",
            "Empirical study of technical debt in open-source projects",
        ],
        "publications": [
            "Menon, D. (2023) 'LLM-Assisted Test Generation at Scale', ICSE.",
            "Menon, D. & Rao, A. (2021) 'Measuring Technical Debt in Practice', TSE.",
        ],
        "experience_years": 17,
        "max_project_slots": 5,
        "current_project_count": 3,
        "past_students": ["Varun Iyer", "Pooja Nambiar", "Siddharth Rao"],
        "email": "deepak.menon@university.edu",
        "office": "CSE Block A, Room 402",
        "biography": (
            "Dr. Deepak Menon bridges classical software engineering research with modern LLM tooling, "
            "studying how AI-assisted development changes software quality and maintainability."
        ),
    },
    {
        "id": "fac_013",
        "name": "Dr. Lakshmi Narayan",
        "designation": "Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Artificial Intelligence", "Knowledge Representation", "Multi-Agent Systems"],
        "keywords": ["planning", "knowledge graphs", "multi-agent systems", "symbolic AI", "neuro-symbolic"],
        "current_projects": [
            "Neuro-symbolic reasoning for scientific discovery",
            "Multi-agent negotiation frameworks for resource allocation",
        ],
        "publications": [
            "Narayan, L. (2022) 'Neuro-Symbolic Reasoning: A Survey', AAAI.",
        ],
        "experience_years": 22,
        "max_project_slots": 4,
        "current_project_count": 3,
        "past_students": ["Harsha Vardhan", "Meenal Joshi"],
        "email": "lakshmi.narayan@university.edu",
        "office": "AI Research Center, Room 5",
        "biography": (
            "Dr. Lakshmi Narayan directs the AI Research Center and has been active in the field since "
            "the early resurgence of neural methods. Her current interest is combining symbolic reasoning "
            "with modern deep learning."
        ),
    },
    {
        "id": "fac_014",
        "name": "Dr. Farhan Ahmed",
        "designation": "Assistant Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Natural Language Processing", "Speech Processing", "Multimodal Learning"],
        "keywords": ["speech recognition", "multimodal models", "text-to-speech", "audio-visual learning"],
        "current_projects": [
            "Multimodal models for accessible audio-visual content",
            "Low-resource speech recognition for regional dialects",
        ],
        "publications": [
            "Ahmed, F. (2024) 'Multimodal Learning for Accessibility Applications', Interspeech.",
        ],
        "experience_years": 4,
        "max_project_slots": 3,
        "current_project_count": 1,
        "past_students": [],
        "email": "farhan.ahmed@university.edu",
        "office": "CSE Block A, Room 210",
        "biography": (
            "Dr. Farhan Ahmed recently joined after completing his PhD on multimodal speech and language "
            "models. He is building out a new lab focused on accessibility-oriented AI."
        ),
    },
    {
        "id": "fac_015",
        "name": "Dr. Neha Kapoor",
        "designation": "Associate Professor",
        "department": "Computer Science & Engineering",
        "research_areas": ["Machine Learning", "Computer Vision", "Generative Models"],
        "keywords": ["GANs", "diffusion models", "image generation", "representation learning"],
        "current_projects": [
            "Diffusion-based synthetic data generation for rare medical conditions",
            "Representation learning for satellite imagery",
        ],
        "publications": [
            "Kapoor, N. (2023) 'Diffusion Models for Rare-Class Medical Data Augmentation', MICCAI.",
        ],
        "experience_years": 8,
        "max_project_slots": 4,
        "current_project_count": 4,
        "past_students": ["Ayesha Malik", "Ravi Teja"],
        "email": "neha.kapoor@university.edu",
        "office": "CSE Block B, Room 150",
        "biography": (
            "Dr. Neha Kapoor works at the boundary of generative modeling and computer vision, with "
            "applications ranging from medical imaging to remote sensing."
        ),
    },
    {
        "id": "fac_016",
        "name": "Dr. Sameer Joshi",
        "designation": "Professor",
        "department": "Electronics & Communication",
        "research_areas": ["Cyber-Physical Systems", "IoT", "Networking"],
        "keywords": ["cyber-physical systems", "industrial IoT", "network protocols", "digital twins"],
        "current_projects": [
            "Digital twin frameworks for smart manufacturing",
            "Secure protocols for industrial IoT deployments",
        ],
        "publications": [
            "Joshi, S. (2021) 'Digital Twins for Cyber-Physical Manufacturing Systems', IEEE TII.",
        ],
        "experience_years": 15,
        "max_project_slots": 3,
        "current_project_count": 2,
        "past_students": ["Chirag Patel"],
        "email": "sameer.joshi@university.edu",
        "office": "ECE Building, Room 88",
        "biography": (
            "Dr. Sameer Joshi's lab builds cyber-physical systems that bridge networking, IoT, and "
            "industrial control, with strong ties to manufacturing industry partners."
        ),
    },
]
