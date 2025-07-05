import json
import re
from datetime import datetime
from llama_cpp import Llama

class PlannerAgent:
    def __init__(self, model_path="Models/phi-2/phi-2.Q5_K_M.gguf"):
        self.llm = Llama(model_path=model_path, n_ctx=4096)
        
        # Domain-specific templates for post-processing
        self.domain_templates = {
            "marketplace": {
                "core_features": [
                    "User authentication and profiles",
                    "Product catalog with advanced filtering",
                    "Shopping cart and wishlist",
                    "Secure payment processing",
                    "Order management and tracking",
                    "Product search and recommendations",
                    "User reviews and ratings",
                    "Admin dashboard for product management"
                ],
                "pages": [
                    {"name": "Home", "components": ["Hero section", "Featured products", "Category navigation", "Footer"]},
                    {"name": "Product Listing", "components": ["Filter sidebar", "Product grid", "Sort options", "Pagination"]},
                    {"name": "Product Detail", "components": ["Product images", "Product info", "Size/color selector", "Add to cart", "Reviews"]},
                    {"name": "Shopping Cart", "components": ["Cart items", "Quantity controls", "Price summary", "Checkout button"]},
                    {"name": "Checkout", "components": ["Shipping form", "Payment form", "Order summary", "Place order"]},
                    {"name": "User Profile", "components": ["Account info", "Order history", "Wishlist", "Address book"]},
                    {"name": "Admin Dashboard", "components": ["Product management", "Order management", "Analytics", "User management"]}
                ],
                "file_structure": {
                    "index.html": "Main HTML entry point",
                    "src/App.js": "Main React app component",
                    "src/components/ProductCard.js": "Individual product display",
                    "src/components/ProductGrid.js": "Grid of products",
                    "src/components/CartItem.js": "Shopping cart item component",
                    "src/components/FilterSidebar.js": "Product filtering interface",
                    "src/components/Header.js": "Navigation header with cart icon",
                    "src/pages/Home.js": "Homepage with featured products",
                    "src/pages/ProductListing.js": "Product catalog page",
                    "src/pages/ProductDetail.js": "Individual product page",
                    "src/pages/Cart.js": "Shopping cart page",
                    "src/pages/Checkout.js": "Checkout flow",
                    "src/pages/Profile.js": "User profile page",
                    "src/pages/Admin.js": "Admin dashboard",
                    "src/api/products.js": "Product API service",
                    "src/api/cart.js": "Cart API service",
                    "src/api/orders.js": "Order management API",
                    "src/api/auth.js": "Authentication API",
                    "src/utils/auth.js": "Authentication utilities",
                    "src/utils/cart.js": "Cart management utilities",
                    "src/hooks/useAuth.js": "Authentication React hook",
                    "src/hooks/useCart.js": "Cart management React hook",
                    "src/styles/globals.css": "Global styles",
                    "src/styles/components.css": "Component-specific styles"
                }
            },
            "dashboard": {
                "core_features": [
                    "User authentication and authorization",
                    "Data visualization and analytics",
                    "Real-time data updates",
                    "Interactive charts and graphs",
                    "Data filtering and search",
                    "Export functionality",
                    "User management",
                    "Settings and configuration"
                ],
                "pages": [
                    {"name": "Dashboard", "components": ["Overview cards", "Charts", "Recent activity", "Quick actions"]},
                    {"name": "Analytics", "components": ["Data charts", "Filters", "Date range picker", "Export tools"]},
                    {"name": "Settings", "components": ["User preferences", "System settings", "Integrations"]},
                    {"name": "Profile", "components": ["User info", "Security settings", "Notification preferences"]}
                ]
            },
            "social": {
                "core_features": [
                    "User profiles and authentication",
                    "Post creation and sharing",
                    "Real-time messaging",
                    "Friend/follower system",
                    "Content feed algorithm",
                    "Media upload and sharing",
                    "Notifications system",
                    "Content moderation"
                ],
                "pages": [
                    {"name": "Feed", "components": ["Post creation", "News feed", "Story highlights", "Trending"]},
                    {"name": "Profile", "components": ["Profile info", "Post grid", "Followers/following", "Settings"]},
                    {"name": "Messages", "components": ["Chat list", "Message thread", "Media sharing", "Online status"]},
                    {"name": "Explore", "components": ["Trending posts", "Suggested users", "Topics", "Search"]}
                ]
            }
        }

    def plan(self, user_goal: str, metadata_file: str = "plan.json") -> list:
        # Detect domain from goal
        domain = self._detect_domain(user_goal)
        
        # Enhanced prompt with domain-specific examples
        prompt = self._create_enhanced_prompt(user_goal, domain)
        
        print(f"[*] Detected domain: {domain}")
        print("[*] Generating detailed multi-agent plan...")
        
        try:
            response = self.llm(prompt, max_tokens=2048, stop=["### END", "# END"])

            output = response["choices"][0]["text"].strip()
            
            # Try to parse the JSON
            parsed_json = json.loads(output)
            
            # Add timestamp
            parsed_json["generated_at"] = datetime.now().isoformat()
            
            # Post-process the plan to make it domain-specific
            parsed_json = self._post_process_plan(parsed_json, user_goal, domain)
            
            print("[✓] Generated plan processed successfully")
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[!] JSON decode error: {e}")
            print(f"[!] Raw output was:\n{output}")
            parsed_json = self._create_domain_specific_fallback(user_goal, domain)

        # Save the plan
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, indent=4)
        print(f"[✓] Plan saved to {metadata_file}")

        return parsed_json.get("planner", {}).get("subtasks", [])

    def _detect_domain(self, goal: str) -> str:
      """Use the LLM to intelligently classify the goal into a domain"""
      domain_prompt = f"""You are an intelligent software project classifier.

      Given the following project goal, classify it into one of the following domains:
      - marketplace
      - dashboard
      - social
      - general

      Only  respond with the domain name (lowercase).

      Goal: "{goal}"
      Domain:"""

      print("[*] Asking LLM to classify domain...")

      try:
        response = self.llm(domain_prompt, max_tokens=5)
        domain = response["choices"][0]["text"].strip().lower()
        if domain not in ["marketplace", "dashboard", "social", "general"]:
            print(f"[!] Unrecognized domain '{domain}', defaulting to 'general'")
            domain = "general"
      except Exception as e:
        print(f"[!] Domain classification failed: {e}, defaulting to 'general'")
        domain = "general"

      print(f"[✓] Detected domain: {domain}")
      return domain



    def _create_enhanced_prompt(self, user_goal: str, domain: str) -> str:
        """Create domain-specific prompt with relevant examples"""
        
        if domain == "marketplace":
            example_goal = "Build a shoe marketplace"
            example_features = ["Product catalog", "Shopping cart", "Payment processing", "User accounts"]
            example_pages = [
                {"name": "Home", "components": ["Featured products", "Category navigation", "Search bar"]},
                {"name": "Product Detail", "components": ["Product images", "Size selector", "Add to cart", "Reviews"]}
            ]
            example_files = {
                "src/components/ProductCard.js": "Individual product display component",
                "src/pages/ProductDetail.js": "Product detail page with images and purchasing options",
                "src/api/products.js": "Product catalog API service"
            }
        elif domain == "dashboard":
            example_goal = "Build an analytics dashboard"
            example_features = ["Data visualization", "Real-time updates", "User management", "Export functionality"]
            example_pages = [
                {"name": "Dashboard", "components": ["Overview cards", "Charts", "Recent activity"]},
                {"name": "Analytics", "components": ["Data charts", "Filters", "Export tools"]}
            ]
            example_files = {
                "src/components/Chart.js": "Reusable chart component",
                "src/pages/Dashboard.js": "Main dashboard with overview",
                "src/api/analytics.js": "Analytics data API service"
            }
        else:
            example_goal = "Build a web application"
            example_features = ["User authentication", "Data management", "User interface", "API integration"]
            example_pages = [
                {"name": "Home", "components": ["Header", "Main content", "Footer"]},
                {"name": "Dashboard", "components": ["Navigation", "Content area"]}
            ]
            example_files = {
                "src/App.js": "Main application component",
                "src/pages/Home.js": "Homepage component",
                "src/api/service.js": "API service layer"
            }

        return f"""
You are a multi-agent planner. Given a software goal, return structured JSON with detailed tasks for planner, coder, and designer.

### BEGIN EXAMPLE ###
Goal: Build a water pollution monitoring dashboard
Output:
{{
  "goal": "Build a water pollution monitoring dashboard",
  "project_type": "dashboard",
  "domain": "environment",
  "planner": {{
    "subtasks": ["Define data inputs", "Choose visualization tools", "Plan backend API"],
    "requirements": {{
      "core_features": ["Live pollution feed", "Historical trends", "Export graphs"],
      "tech_stack": "React + Flask + PostgreSQL",
      "timeline": "3 weeks"
    }}
  }},
  "coder": {{
    "tasks": ["Create chart components", "Set up PostgreSQL schema", "Integrate pollution API"],
    "technical_specs": {{
      "frontend": "React.js",
      "backend": "Flask",
      "database": "PostgreSQL",
      "deployment": "Heroku"
    }},
    "file_structure": {{
      "src/pages/Dashboard.js": "Main dashboard view",
      "src/api/pollution.js": "API layer for pollution data",
      "src/components/ChartCard.js": "Reusable chart"
    }}
  }},
  "designer": {{
    "theme": "Scientific clean UI with blue-green palette",
    "pages": [
      {{"name": "Dashboard", "components": ["Map", "Charts", "Export"]}}
    ],
    "design_system": {{
      "colors": {{"primary": "#2196F3", "secondary": "#4CAF50"}},
      "typography": {{"headings": "Roboto", "body": "Open Sans"}}
    }}
  }}
}}
### END EXAMPLE ###

# ACTUAL GOAL FOLLOWS
Goal: {user_goal}
Output:
"""




    def _post_process_plan(self, plan: dict, goal: str, domain: str) -> dict:
        """Post-process the plan to make it more domain-specific"""
        
        # If the plan is too generic, enhance it with domain-specific content
        if self._is_plan_too_generic(plan):
            print("[*] Plan seems generic, enhancing with domain-specific content...")
            plan = self._enhance_with_domain_content(plan, goal, domain)
        
        # Always ensure critical fields are present
        plan = self._ensure_critical_fields(plan, goal, domain)
        
        return plan

    def _is_plan_too_generic(self, plan: dict) -> bool:
        """Check if the plan is too generic"""
        generic_indicators = [
            "To be defined based on goal",
            "Modern web technologies",
            "Main content",
            "Content area"
        ]
        
        plan_str = json.dumps(plan).lower()
        return any(indicator.lower() in plan_str for indicator in generic_indicators)

    def _enhance_with_domain_content(self, plan: dict, goal: str, domain: str) -> dict:
        """Enhance plan with domain-specific content"""
        
        if domain in self.domain_templates:
            template = self.domain_templates[domain]
            
            # Enhance core features
            if "requirements" in plan.get("planner", {}):
                plan["planner"]["requirements"]["core_features"] = template["core_features"]
            
            # Enhance pages
            if "pages" in plan.get("designer", {}):
                plan["designer"]["pages"] = template["pages"]
            
            # Enhance file structure
            if "file_structure" in plan.get("coder", {}):
                plan["coder"]["file_structure"] = template["file_structure"]
        
        return plan

    def _ensure_critical_fields(self, plan: dict, goal: str, domain: str) -> dict:
        """Ensure all critical fields are present"""
        
        # Add domain to plan
        plan["domain"] = domain
        
        # Ensure planner requirements
        if "planner" not in plan:
            plan["planner"] = {}
        if "requirements" not in plan["planner"]:
            plan["planner"]["requirements"] = {}
        
        # Ensure coder file_structure
        if "coder" not in plan:
            plan["coder"] = {}
        if "file_structure" not in plan["coder"] and domain in self.domain_templates:
            plan["coder"]["file_structure"] = self.domain_templates[domain]["file_structure"]
        
        # Ensure designer pages
        if "designer" not in plan:
            plan["designer"] = {}
        if "pages" not in plan["designer"] and domain in self.domain_templates:
            plan["designer"]["pages"] = self.domain_templates[domain]["pages"]
        
        return plan

    def _create_domain_specific_fallback(self, goal: str, domain: str) -> dict:
        """Create a domain-specific fallback plan"""
        
        base_plan = {
            "goal": goal,
            "project_type": "web_application",
            "domain": domain,
            "planner": {
                "subtasks": [
                    f"Define {domain} requirements and user stories",
                    "Research relevant APIs and third-party services",
                    f"Plan technical architecture for {domain} application",
                    "Create development timeline and milestones"
                ],
                "requirements": {
                    "core_features": ["To be defined based on goal"],
                    "tech_stack": "React.js frontend, Node.js backend, PostgreSQL database",
                    "timeline": "3-4 weeks"
                }
            },
            "coder": {
                "tasks": [
                    "Set up project structure with chosen framework",
                    f"Implement {domain}-specific business logic",
                    "Build user interface components",
                    "Add data persistence layer",
                    "Implement API integrations",
                    "Add authentication and testing"
                ],
                "technical_specs": {
                    "frontend": "React.js with TypeScript",
                    "backend": "Node.js/Express",
                    "database": "PostgreSQL",
                    "deployment": "Vercel"
                }
            },
            "designer": {
                "theme": f"Modern, clean design optimized for {domain} use case",
                "pages": [],
                "design_system": {
                    "colors": {"primary": "#007bff", "secondary": "#6c757d"},
                    "typography": {"headings": "Inter Bold", "body": "Inter Regular"}
                }
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # Add domain-specific content if available
        if domain in self.domain_templates:
            template = self.domain_templates[domain]
            base_plan["planner"]["requirements"]["core_features"] = template["core_features"]
            base_plan["coder"]["file_structure"] = template["file_structure"]
            base_plan["designer"]["pages"] = template["pages"]
        
        return base_plan

if __name__ == "__main__":
    planner = PlannerAgent()
    goal = "Build a Social media platform for animals with user authentication, chatting, user creation, and video creation"
    tasks = planner.plan(goal)
    print("Generated planner tasks:")
    for task in tasks:
        print(f"- {task}")