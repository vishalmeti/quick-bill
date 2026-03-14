# Product Overview – Mini ERP for Local Businesses

## 1. Product Summary

Mini ERP is a lightweight business management platform designed for **small local businesses** that currently manage operations through **WhatsApp chats, notebooks, or spreadsheets**.

The goal of this product is to provide a **simple, mobile-friendly system** that helps business owners track inventory, sales, profits, and customer credits without needing technical knowledge.

The system should be extremely easy to use, fast, and minimal. Most users will be **shop owners with limited time and limited technical skills**.

Examples of target users include:

* Grocery store owners
* Salon owners
* Mechanics
* Bakeries
* Small retail shops

The platform will help them replace manual tracking with a **digital system that automates daily operations**.

The system will follow a **microservice architecture with FastAPI services and DynamoDB databases**.

The MVP version should focus on **core functionality only** and avoid unnecessary complexity.

---

# 2. Core Problems Being Solved

Small businesses commonly face the following problems:

1. Inventory is tracked manually or not tracked at all.
2. Daily profit calculation is done manually.
3. Customer credit (udhaar) is difficult to track.
4. Invoices are often sent manually via WhatsApp.
5. Sales records are scattered across notebooks or chats.

This product solves these problems by providing a **simple centralized system**.

---

# 3. Target Users

Primary users of the system:

Small business owners who:

* operate small shops
* track inventory manually
* provide credit to customers
* communicate with customers through WhatsApp

The platform should prioritize:

* simplicity
* fast workflows
* minimal clicks
* mobile-first usability

---

# 4. Core Features (MVP)

The MVP version should only include the following features.

## Business Registration

A business owner can create an account and register their business.

The system stores:

* business name
* business type (salon, grocery, bakery, mechanic etc.)

The owner can later add employees.

---

## Product / Inventory Management

The user can create products or items sold in their shop.

Each product contains:

* product name
* price
* category (optional)
* stock quantity

The system must allow:

* adding products
* updating stock
* viewing current inventory

---

## Sales Recording

When a customer buys items, the owner can record a sale.

A sale contains:

* multiple items
* quantity per item
* total amount
* payment type (cash / online / credit)

The system will:

* store the sale
* reduce product stock
* calculate total amount automatically

---

## Customer Credit Tracking

Some customers buy products on credit.

The system should allow:

* recording credit sales
* tracking outstanding credit for each customer
* updating credit when payment is received

Customer identification will initially be based on **phone number**.

---

## Daily Profit Calculation

The system should automatically calculate:

* total daily sales
* total revenue
* basic profit metrics

This should be derived from recorded sales data.

---

## WhatsApp Invoice Sending

After a sale is completed, the system can generate a **simple invoice message**.

The message will be sent to the customer via **WhatsApp API integration**.

The invoice will include:

* items purchased
* quantities
* total amount
* business name

---

# 5. Product Architecture

The backend will follow a **simple microservice architecture**.

The goal is to maintain separation of responsibilities while keeping the system easy to build and maintain.

Core services:

Auth Service
Handles authentication, user accounts, and business registration.

Inventory Service
Manages products and stock levels.

Billing / Sales Service
Handles sales recording, invoices, and profit calculations.

Notification Service
Handles sending WhatsApp messages and notifications.

API Gateway
A FastAPI gateway that routes requests to internal services.

Each service should maintain its **own DynamoDB tables** to keep services loosely coupled.

---

# 6. Technology Stack

Backend Framework
FastAPI

Database
Amazon DynamoDB

Architecture Style
Microservices

Service Communication
REST APIs

Containerization
Docker

Future orchestration
Kubernetes or AWS ECS

Messaging (future improvement)
SQS or event-driven communication

---

# 7. Monetization Model

The platform will use a **monthly subscription model**.

Pricing tiers:

₹199/month – basic features
₹499/month – advanced features (future)

Potential advanced features may include:

* analytics
* multi-store management
* supplier management
* advanced reporting
* employee permissions

---

# 8. Design Principles

The product must follow these principles:

Simplicity first
Avoid feature overload.

Mobile-first design
Most users will use phones.

Fast operations
Adding a sale should take only a few seconds.

Minimal configuration
Users should not need technical setup.

Scalable architecture
Microservices should allow easy expansion later.

---

# 9. MVP Scope

The MVP version should support the following workflow:

1. Business owner registers
2. Owner adds products
3. Owner records a sale
4. Stock is automatically updated
5. Sale is saved
6. Invoice is sent via WhatsApp
7. Daily sales can be viewed

Anything beyond this should be considered **future scope**.

---

# 10. Future Expansion Possibilities

After the MVP is stable, the platform can expand with:

Analytics Service
Business performance dashboards.

Subscription Service
Billing and plan management.

Customer Service
Customer profiles and loyalty programs.

Supplier Service
Purchase orders and restocking.

AI Insights
Sales forecasting and inventory recommendations.

These should not be included in the initial version.

---

# 11. Key Product Philosophy

This product is designed for **speed, simplicity, and practicality**.

If a feature makes the product complicated for small shop owners, it should be avoided.

The system should feel like a **digital notebook with automation**, not a complex enterprise ERP.
