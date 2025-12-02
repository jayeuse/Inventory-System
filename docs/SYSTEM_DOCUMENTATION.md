# Inventory and Integrated POS System
## Technical Documentation

---

## 1.1 BACKGROUND

### Overview

The **Inventory and Integrated POS System** is a comprehensive solution engineered to modernize and streamline the complex management processes inherent in a pharmacy environment. Traditional inventory methodologies often rely on repetitive manual tasks—such as tracking quantities, monitoring expiration dates, and recording scattered transactions—which are highly susceptible to human error, operational delays, and data inconsistencies.

### Project Objectives

This project aims to provide a centralized, automated, and user-centric solution with the following primary objectives:

| Objective | Description |
|-----------|-------------|
| **Optimize Stock Monitoring** | Ensure accurate, real-time tracking of inventory levels across all product batches |
| **Mitigate Risk** | Reduce human error and prevent revenue loss through automated expiration management and low-stock alerts |
| **Enhance Security** | Implement modern authentication protocols including Multi-Factor Authentication (MFA) and One-Time Passwords (OTP) |
| **Provide Intelligence** | Offer real-time analytics on inventory health, stock status distribution, and point-of-sale performance |

### System Components

The solution comprises two synchronized platforms that share a unified backend:

```
┌─────────────────────────────────────────────────────────────────┐
│                        UNIFIED BACKEND                          │
│                    (Django + PostgreSQL)                        │
├─────────────────────────────┬───────────────────────────────────┤
│      INVENTORY SYSTEM       │     INTEGRATED POS SYSTEM         │
│  ─────────────────────────  │  ───────────────────────────────  │
│  Administrative backbone    │  Front-line sales interface       │
│  managing:                  │  handling:                        │
│  • Product lifecycles       │  • Sales operations               │
│  • Procurement              │  • Real-time stock queries        │
│  • Supplier relations       │  • Transaction processing         │
│  • Master data              │  • Instant inventory updates      │
└─────────────────────────────┴───────────────────────────────────┘
```

---

## 1.2 SCOPE OF THE PROJECT

The project encompasses end-to-end workflows required for pharmacy operations, divided into two primary environments:

### A. Inventory System Modules

#### 1. Authentication & Security Module
- **User Roles:** Admin, Staff, and Clerk with role-based permissions
- **Authentication:** Secure login via Google OAuth with OTP verification
- **Recovery:** OTP-based "Forgot Password" recovery flow

#### 2. Dashboard Module
Provides a high-level view of system health through visual analytics:
- **Category Distribution:** Pie Chart visualization
- **Top Suppliers:** Bar Graph representation
- **Stock Health Status:** Donut Chart (Normal, Low Stock, Out of Stock, Near Expiry, Expired)
- **Activity Feed:** Real-time log of recent system activities

#### 3. Products Module
Comprehensive registry for product master data:
- Product ID (auto-generated: PRD-XXXXX)
- Brand Name & Generic Name
- Category & Sub-category classification
- Unit Price & Unit of Measurement
- Expiry & Low Stock thresholds

#### 4. Inventory Module
Central hub for stock management with three sub-modules:

| Sub-Module | Function |
|------------|----------|
| **Stocks List** | Master view of stock IDs and total on-hand quantities |
| **Batches List** | Granular control over individual batches with expiry tracking |
| **Orders** | Multi-supplier ordering and receiving (Stock In operations) |

#### 5. Transactions Module
Unified ledger of all inventory movements:
- **Stock In (IN):** Order receipts and inventory additions
- **Stock Out (OUT):** POS sales and inventory deductions
- **Adjustments (ADJ):** Manual corrections and reconciliations

#### 6. Settings Module
Administrative control panel for:
- System Settings (timezone, currency)
- Category & Subcategory Management
- Supplier Management

### B. Integrated POS System Modules

#### 1. Sales Module
- Browse products by category
- Process sales efficiently
- Automatic stock deductions in real-time

#### 2. Items Module
- Live view of all active products
- Real-time availability status
- Category-based filtering

#### 3. Transactions Module
- Complete history of POS sales
- Granular transaction details for auditing
- Search and filter capabilities

#### 4. Back Office Analytics
- Sales trends visualization
- Top-selling categories
- Product movement summaries

---

## 1.3 TECHNOLOGY STACK

The system utilizes a robust, open-source stack designed for scalability and security:

### Front End Technologies

| Technology | Purpose |
|------------|---------|
| **HTML5** | Semantic structure and content markup |
| **CSS3 / Bootstrap 5** | Responsive, mobile-ready styling and layout |
| **JavaScript (ES6+)** | Client-side interactivity, dynamic UI rendering, and API consumption |

### Back End Technologies

| Technology | Purpose |
|------------|---------|
| **Django Framework 4.x** | Core Python-based web framework for server-side logic and routing |
| **Django REST Framework** | RESTful API endpoints connecting front-end and database |
| **Python 3.10+** | Primary programming language |

### Database

| Technology | Purpose |
|------------|---------|
| **PostgreSQL 14+** | Relational database ensuring data integrity for complex relationships |
| **Django ORM** | Abstraction layer for secure, efficient database queries |

### External APIs

| Service | Purpose |
|---------|---------|
| **Google OAuth 2.0** | Secure identity verification and SSO capabilities |
| **Google Authenticator API** | Two-factor authentication and OTP generation |
| **Gmail API** | OTP delivery via email |

---

## 1.4 ARCHITECTURAL DESIGN

The system utilizes a robust **Multi-Tier Architecture** (specifically a Three-Tier pattern with an External Services layer) designed to ensure separation of concerns, scalability, and maintainability. This architectural style decouples the user interface from the business logic and data storage, allowing for independent updates and modular development.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES LAYER                              │
│                    Google OAuth 2.0 / Authenticator API                      │
│                  • OTP Generation  • MFA  • Password Recovery                │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                         PRESENTATION LAYER (Client)                          │
│   ┌─────────────────────────┐     ┌─────────────────────────┐               │
│   │   Inventory Dashboard   │     │   Integrated POS        │               │
│   │   (Admin/Staff View)    │     │   (Clerk View)          │               │
│   └─────────────────────────┘     └─────────────────────────┘               │
│                    Technology: HTML5 | CSS3 | Bootstrap | JavaScript         │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ RESTful API (JSON/HTTPS)
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                         APPLICATION LAYER (Business Logic)                   │
│                                                                              │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐     │
│   │  API Endpoints  │  │ Business Logic  │  │  Access Control (RBAC)  │     │
│   │  /api/auth/     │  │ Stock Deduction │  │  Session Validation     │     │
│   │  /api/products/ │  │ Batch Expiry    │  │  Permission Checks      │     │
│   │  /api/inventory/│  │ Order Process   │  │  Token Authentication   │     │
│   │  /api/pos/      │  │ Analytics       │  │                         │     │
│   └─────────────────┘  └─────────────────┘  └─────────────────────────┘     │
│                         Technology: Django + Django REST Framework           │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ Django ORM
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                         DATA PERSISTENCE LAYER (Database)                    │
│                                                                              │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐               │
│   │   Users    │ │  Products  │ │  Inventory │ │   Orders   │               │
│   │   & Auth   │ │  Catalog   │ │  & Batches │ │   & Txns   │               │
│   └────────────┘ └────────────┘ └────────────┘ └────────────┘               │
│                              Technology: PostgreSQL                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Layer Descriptions

#### 1. Presentation Layer (Client-Side)
This layer acts as the interface between the user and the system, responsible for visual rendering of dashboards, forms, and interactive elements.

- **Technology:** HTML5, CSS3 (Bootstrap), JavaScript
- **Function:** Operates as a "Thin Client" focusing on display logic
- **Behavior:** Captures user inputs and asynchronously transmits them to the backend via RESTful API requests
- **Components:** Dashboard analytics, POS sales interface, Product management forms

#### 2. Application Layer (Business Logic)
The core intelligence of the system resides here. This layer processes requests from the client, enforces business rules, and bridges to the database.

- **Technology:** Django Framework, Django REST Framework (DRF)
- **Key Responsibilities:**
  - **API Exposure:** Secure endpoints for authentication, inventory control, and transaction processing
  - **Logic Execution:** Complex calculations (stock deduction upon sale, batch expiry status calculation)
  - **Access Control:** Session validation and Role-Based Access Control (RBAC) enforcement

#### 3. Data Persistence Layer (Database)
This layer manages storage, retrieval, and integrity of all persistent data.

- **Technology:** PostgreSQL managed via Django ORM
- **Function:** Stores structured data including Product Catalogs, Stock Batches, Supplier Records, and Transaction Logs
- **Integrity:** Django ORM abstractions ensure secure SQL execution, preventing injection attacks and maintaining relational consistency

#### 4. External Services Integration
This layer manages secure communications with third-party providers.

- **Technology:** Google OAuth 2.0 / Authenticator API
- **Function:** Offloads sensitive security processes such as OTP generation, multi-factor authentication, and secure password recovery

### System Interoperability & Data Flow

The architecture ensures real-time synchronization between the two primary subsystems:

```
┌─────────────────┐                         ┌─────────────────┐
│  POS SYSTEM     │                         │ INVENTORY ADMIN │
│  (Sale Event)   │                         │  (Dashboard)    │
└────────┬────────┘                         └────────▲────────┘
         │                                           │
         │ 1. POST /api/pos/sale                     │ 4. Real-time
         │                                           │    Reflection
         ▼                                           │
┌─────────────────────────────────────────────────────────────┐
│                    UNIFIED BACKEND                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 2. Process Sale:                                     │    │
│  │    • Validate stock availability                     │    │
│  │    • Deduct from batch (FIFO by expiry)             │    │
│  │    • Update product_stocks.total_on_hand            │    │
│  │    • Create transaction record (type: OUT)          │    │
│  │    • Update batch/stock status if needed            │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 3. Database Updates:                                 │    │
│  │    • transaction table: +1 record                    │    │
│  │    • product_batch table: -quantity                  │    │
│  │    • product_stocks table: -quantity                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Key Integration Points:**
- **Unified Backend:** Both Inventory Dashboard and POS Interface consume the same API
- **Event-Driven Updates:** A "Sale" event triggers immediate write operations to both Transaction and Stock tables
- **Instant Reflection:** Stock deductions via POS are instantly reflected in the Inventory Dashboard without manual reconciliation

---

## 1.5 DATABASE SCHEMA

The system uses a relational database with the following entity groups:

### Entity Relationship Summary

| Entity Group | Tables | Description |
|--------------|--------|-------------|
| **User Management** | `auth_user`, `user_information`, `otp` | User accounts, profiles, and authentication |
| **Product Catalog** | `category`, `subcategory`, `product` | Product classification and master data |
| **Supplier Management** | `supplier`, `supplier_product` | Supplier information and product associations |
| **Inventory Control** | `product_stocks`, `product_batch` | Stock levels and batch tracking with expiry |
| **Order Management** | `order`, `order_item`, `receive_order` | Purchase orders and receiving |
| **Transaction Logging** | `transaction` | All inventory movements (IN/OUT/ADJ) |
| **System/Audit** | `archive_log` | Soft-delete and audit trail |

### Key Relationships

```
auth_user (Django) ←──── user_information (1:1 extension)
     │
     └──────────────────► otp (1:N for authentication)

category ──► subcategory ──► product
                                │
                                ├──► product_stocks ──► product_batch
                                │
                                └──► supplier_product ◄── supplier

order ──► order_item ──► receive_order
              │
              └──────────────────────► transaction ◄── product_batch
```

> **Note:** See `docs/DATABASE_ERD.dbml` for the complete database schema in DBML format (viewable at dbdiagram.io).

---

## 1.6 SECURITY CONSIDERATIONS

### Authentication Flow

1. User enters credentials (username/password)
2. System validates against `auth_user` table
3. OTP generated and sent via Gmail API
4. User enters OTP for verification
5. Session token issued upon successful verification
6. Role-based permissions applied based on `user_information.role`

### Security Features

- **Password Hashing:** Django's PBKDF2 algorithm with SHA256
- **CSRF Protection:** Django's built-in CSRF middleware
- **SQL Injection Prevention:** Django ORM parameterized queries
- **XSS Protection:** Template auto-escaping
- **Session Security:** Secure, HTTP-only cookies
- **RBAC:** Three-tier role system (Admin, Staff, Clerk)

---

## 1.7 DEPLOYMENT REQUIREMENTS

### Minimum System Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.10 or higher |
| **PostgreSQL** | 14.0 or higher |
| **RAM** | 4GB minimum (8GB recommended) |
| **Storage** | 20GB minimum |

### Required Python Packages

See `requirements.txt` for the complete dependency list.

---

*Document Version: 1.0*
*Last Updated: December 2, 2025*
