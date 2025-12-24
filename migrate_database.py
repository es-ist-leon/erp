#!/usr/bin/env python3
"""
Database Migration Script for HolzbauERP
Adds all new columns to existing tables
"""

import psycopg2
from psycopg2 import sql
import sys

# Database connection
DB_CONFIG = {
    'host': 'public-master-zmbdbeybepes.db.upclouddatabases.com',
    'port': 11569,
    'user': 'upadmin',
    'password': 'AVNS_j5p8EGB21QxeE1u-Fc3',
    'dbname': 'defaultdb',
    'sslmode': 'require'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def column_exists(cursor, table, column):
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        )
    """, (table, column))
    return cursor.fetchone()[0]

def add_column_if_not_exists(cursor, table, column, data_type, default=None):
    if not column_exists(cursor, table, column):
        if default is not None:
            query = f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {data_type} DEFAULT %s'
            cursor.execute(query, (default,))
        else:
            query = f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {data_type}'
            cursor.execute(query)
        print(f"  + Added {table}.{column}")
        return True
    return False

def migrate_tenants(cursor):
    """Add new columns to tenants table"""
    print("\n📋 Migrating tenants table...")
    
    columns = [
        ('legal_form', 'VARCHAR(50)', None),
        ('founding_date', 'DATE', None),
        ('tax_number', 'VARCHAR(50)', None),
        ('trade_register_court', 'VARCHAR(100)', None),
        ('chamber_of_crafts', 'VARCHAR(100)', None),
        ('chamber_membership_number', 'VARCHAR(50)', None),
        ('ceo_name', 'VARCHAR(100)', None),
        ('authorized_signatories', 'TEXT', None),
        ('phone_secondary', 'VARCHAR(30)', None),
        ('fax', 'VARCHAR(30)', None),
        ('mobile', 'VARCHAR(30)', None),
        ('linkedin_url', 'VARCHAR(255)', None),
        ('facebook_url', 'VARCHAR(255)', None),
        ('instagram_url', 'VARCHAR(255)', None),
        ('xing_url', 'VARCHAR(255)', None),
        ('address_addition', 'VARCHAR(100)', None),
        ('district', 'VARCHAR(100)', None),
        ('state', 'VARCHAR(100)', None),
        ('country_code', 'VARCHAR(3)', None),
        ('latitude', 'DECIMAL(10,8)', None),
        ('longitude', 'DECIMAL(11,8)', None),
        ('altitude', 'DECIMAL(8,2)', None),
        ('bank_account_holder', 'VARCHAR(100)', None),
        ('secondary_bank_name', 'VARCHAR(100)', None),
        ('secondary_iban', 'VARCHAR(34)', None),
        ('secondary_bic', 'VARCHAR(11)', None),
        ('paypal_email', 'VARCHAR(255)', None),
        ('stripe_account_id', 'VARCHAR(100)', None),
        ('certifications', 'TEXT', None),
        ('quality_management', 'VARCHAR(100)', None),
        ('environmental_certification', 'VARCHAR(100)', None),
        ('safety_certification', 'VARCHAR(100)', None),
        ('master_craftsman_certificate', 'VARCHAR(100)', None),
        ('master_craftsman_name', 'VARCHAR(100)', None),
        ('guild_membership', 'VARCHAR(100)', None),
        ('trade_association', 'VARCHAR(100)', None),
        ('liability_insurance', 'VARCHAR(100)', None),
        ('liability_coverage', 'DECIMAL(15,2)', None),
        ('building_insurance', 'VARCHAR(100)', None),
        ('professional_indemnity', 'VARCHAR(100)', None),
        ('insurance_policy_number', 'VARCHAR(50)', None),
        ('insurance_valid_until', 'DATE', None),
        ('employee_count', 'INTEGER', None),
        ('apprentice_count', 'INTEGER', None),
        ('annual_revenue', 'DECIMAL(15,2)', None),
        ('production_facility_address', 'TEXT', None),
        ('storage_facility_address', 'TEXT', None),
        ('wood_types_offered', 'TEXT', None),
        ('specializations', 'TEXT', None),
        ('service_radius_km', 'INTEGER', None),
        ('invoice_prefix', 'VARCHAR(20)', None),
        ('invoice_number_format', 'VARCHAR(50)', None),
        ('next_invoice_number', 'INTEGER', '1'),
        ('offer_prefix', 'VARCHAR(20)', None),
        ('offer_validity_days', 'INTEGER', '30'),
        ('default_payment_terms', 'INTEGER', '30'),
        ('default_vat_rate', 'DECIMAL(5,2)', '19.00'),
        ('default_currency', 'VARCHAR(3)', 'EUR'),
        ('invoice_footer_text', 'TEXT', None),
        ('email_signature', 'TEXT', None),
        ('smtp_host', 'VARCHAR(255)', None),
        ('smtp_port', 'INTEGER', None),
        ('smtp_user', 'VARCHAR(255)', None),
        ('smtp_password', 'VARCHAR(255)', None),
        ('smtp_use_tls', 'BOOLEAN', 'true'),
        ('working_hours_start', 'TIME', None),
        ('working_hours_end', 'TIME', None),
        ('working_days', 'VARCHAR(20)', None),
        ('fiscal_year_start_month', 'INTEGER', '1'),
        ('data_retention_years', 'INTEGER', '10'),
        ('gdpr_contact_email', 'VARCHAR(255)', None),
        ('custom_fields', 'JSONB', None),
        ('extra_data', 'JSONB', None),
    ]
    
    added = 0
    for col_name, col_type, default in columns:
        if add_column_if_not_exists(cursor, 'tenants', col_name, col_type, default):
            added += 1
    
    print(f"  ✓ Tenants: {added} columns added")

def migrate_projects(cursor):
    """Add new columns to projects table - FULL enterprise schema"""
    print("\n📋 Migrating projects table...")
    
    columns = [
        # Basic info
        ('short_description', 'VARCHAR(500)', None),
        ('sub_status', 'VARCHAR(100)', None),
        
        # Team
        ('project_manager_id', 'UUID', None),
        ('site_manager_id', 'UUID', None),
        ('sales_person_id', 'UUID', None),
        
        # External parties
        ('architect_name', 'VARCHAR(255)', None),
        ('architect_company', 'VARCHAR(255)', None),
        ('architect_email', 'VARCHAR(255)', None),
        ('architect_phone', 'VARCHAR(50)', None),
        ('structural_engineer_name', 'VARCHAR(255)', None),
        ('structural_engineer_company', 'VARCHAR(255)', None),
        ('structural_engineer_email', 'VARCHAR(255)', None),
        ('structural_engineer_phone', 'VARCHAR(50)', None),
        ('energy_consultant_name', 'VARCHAR(255)', None),
        ('energy_consultant_company', 'VARCHAR(255)', None),
        ('general_contractor_name', 'VARCHAR(255)', None),
        ('general_contractor_company', 'VARCHAR(255)', None),
        
        # Dates
        ('inquiry_date', 'DATE', None),
        ('quote_date', 'DATE', None),
        ('quote_deadline', 'DATE', None),
        ('decision_date', 'DATE', None),
        ('order_date', 'DATE', None),
        ('contract_signing_date', 'DATE', None),
        ('planning_start', 'DATE', None),
        ('planning_end', 'DATE', None),
        ('production_start', 'DATE', None),
        ('production_end', 'DATE', None),
        ('delivery_date', 'DATE', None),
        ('planned_start', 'DATE', None),
        ('planned_end', 'DATE', None),
        ('actual_start', 'DATE', None),
        ('actual_end', 'DATE', None),
        ('acceptance_date', 'DATE', None),
        ('warranty_end_date', 'DATE', None),
        
        # Site address
        ('site_name', 'VARCHAR(255)', None),
        ('site_street', 'VARCHAR(255)', None),
        ('site_street_number', 'VARCHAR(20)', None),
        ('site_address_addition', 'VARCHAR(100)', None),
        ('site_postal_code', 'VARCHAR(20)', None),
        ('site_city', 'VARCHAR(100)', None),
        ('site_district', 'VARCHAR(100)', None),
        ('site_state', 'VARCHAR(100)', None),
        ('site_country', 'VARCHAR(100)', 'Deutschland'),
        
        # Geo
        ('site_latitude', 'VARCHAR(20)', None),
        ('site_longitude', 'VARCHAR(20)', None),
        ('site_altitude', 'VARCHAR(20)', None),
        ('site_geohash', 'VARCHAR(20)', None),
        ('site_parcel_number', 'VARCHAR(50)', None),
        ('site_cadastral_district', 'VARCHAR(100)', None),
        ('site_land_register', 'VARCHAR(100)', None),
        ('site_what3words', 'VARCHAR(100)', None),
        
        # Site access
        ('site_access_description', 'TEXT', None),
        ('site_access_restrictions', 'TEXT', None),
        ('site_access_width_m', 'VARCHAR(10)', None),
        ('site_access_height_m', 'VARCHAR(10)', None),
        ('site_access_weight_limit', 'VARCHAR(10)', None),
        ('site_crane_setup_possible', 'BOOLEAN', 'true'),
        ('site_crane_setup_location', 'TEXT', None),
        ('site_storage_area_available', 'BOOLEAN', 'true'),
        ('site_storage_area_sqm', 'VARCHAR(20)', None),
        ('site_electricity_available', 'BOOLEAN', 'false'),
        ('site_water_available', 'BOOLEAN', 'false'),
        ('site_toilet_available', 'BOOLEAN', 'false'),
        ('site_parking_description', 'TEXT', None),
        ('site_special_conditions', 'TEXT', None),
        
        # Building data
        ('building_class', 'VARCHAR(50)', None),
        ('building_use', 'VARCHAR(100)', None),
        ('gross_floor_area', 'VARCHAR(20)', None),
        ('net_floor_area', 'VARCHAR(20)', None),
        ('living_space', 'VARCHAR(20)', None),
        ('usable_area', 'VARCHAR(20)', None),
        ('basement_area', 'VARCHAR(20)', None),
        ('roof_area', 'VARCHAR(20)', None),
        ('facade_area', 'VARCHAR(20)', None),
        ('floors_above_ground', 'INTEGER', None),
        ('floors_below_ground', 'INTEGER', None),
        ('attic_type', 'VARCHAR(50)', None),
        ('building_length_m', 'VARCHAR(20)', None),
        ('building_width_m', 'VARCHAR(20)', None),
        ('building_height_m', 'VARCHAR(20)', None),
        ('ridge_height_m', 'VARCHAR(20)', None),
        ('eaves_height_m', 'VARCHAR(20)', None),
        
        # Roof
        ('roof_type', 'VARCHAR(50)', None),
        ('roof_pitch', 'VARCHAR(20)', None),
        ('roof_pitch_secondary', 'VARCHAR(20)', None),
        ('roof_overhang_eaves', 'VARCHAR(20)', None),
        ('roof_overhang_gable', 'VARCHAR(20)', None),
        ('roof_covering', 'VARCHAR(100)', None),
        
        # Wood technical
        ('wood_volume_m3', 'VARCHAR(20)', None),
        ('wood_type_primary', 'VARCHAR(100)', None),
        ('wood_type_secondary', 'VARCHAR(100)', None),
        ('wood_quality', 'VARCHAR(50)', None),
        ('wood_moisture', 'VARCHAR(20)', None),
        ('wood_certification', 'VARCHAR(50)', None),
        ('wall_construction', 'VARCHAR(100)', None),
        ('wall_thickness_cm', 'VARCHAR(20)', None),
        ('ceiling_construction', 'VARCHAR(100)', None),
        ('roof_construction', 'VARCHAR(100)', None),
        ('prefabrication_degree', 'VARCHAR(50)', None),
        ('module_count', 'INTEGER', None),
        
        # Energy
        ('insulation_standard', 'VARCHAR(50)', None),
        ('energy_efficiency_class', 'VARCHAR(10)', None),
        ('primary_energy_demand', 'VARCHAR(20)', None),
        ('heating_demand', 'VARCHAR(20)', None),
        ('u_value_wall', 'VARCHAR(20)', None),
        ('u_value_roof', 'VARCHAR(20)', None),
        ('u_value_floor', 'VARCHAR(20)', None),
        ('blower_door_value', 'VARCHAR(20)', None),
        ('heating_system', 'VARCHAR(100)', None),
        ('ventilation_system', 'VARCHAR(100)', None),
        ('solar_system', 'VARCHAR(100)', None),
        
        # Permits
        ('building_permit_required', 'BOOLEAN', 'true'),
        ('building_permit_number', 'VARCHAR(100)', None),
        ('building_permit_date', 'DATE', None),
        ('building_permit_authority', 'VARCHAR(255)', None),
        ('building_permit_status', 'VARCHAR(50)', None),
        ('structural_approval', 'VARCHAR(100)', None),
        ('structural_approval_date', 'DATE', None),
        ('fire_safety_concept', 'BOOLEAN', 'false'),
        ('fire_resistance_class', 'VARCHAR(20)', None),
        ('noise_protection_class', 'VARCHAR(20)', None),
        ('earthquake_zone', 'VARCHAR(20)', None),
        ('snow_load_zone', 'VARCHAR(20)', None),
        ('wind_load_zone', 'VARCHAR(20)', None),
        
        # Finance
        ('estimated_value', 'VARCHAR(20)', None),
        ('quoted_value', 'VARCHAR(20)', None),
        ('contract_value', 'VARCHAR(20)', None),
        ('final_value', 'VARCHAR(20)', None),
        ('budget_materials', 'VARCHAR(20)', None),
        ('budget_labor', 'VARCHAR(20)', None),
        ('budget_external', 'VARCHAR(20)', None),
        ('budget_other', 'VARCHAR(20)', None),
        ('actual_cost_materials', 'VARCHAR(20)', None),
        ('actual_cost_labor', 'VARCHAR(20)', None),
        ('actual_cost_external', 'VARCHAR(20)', None),
        ('margin_percent', 'VARCHAR(10)', None),
        ('margin_amount', 'VARCHAR(20)', None),
        ('subsidy_program', 'VARCHAR(255)', None),
        ('subsidy_amount', 'VARCHAR(20)', None),
        ('subsidy_status', 'VARCHAR(50)', None),
        
        # Hours
        ('planned_hours_total', 'VARCHAR(20)', None),
        ('planned_hours_planning', 'VARCHAR(20)', None),
        ('planned_hours_production', 'VARCHAR(20)', None),
        ('planned_hours_assembly', 'VARCHAR(20)', None),
        ('actual_hours_total', 'VARCHAR(20)', None),
        ('actual_hours_planning', 'VARCHAR(20)', None),
        ('actual_hours_production', 'VARCHAR(20)', None),
        ('actual_hours_assembly', 'VARCHAR(20)', None),
        
        # Progress
        ('progress_overall', 'INTEGER', '0'),
        ('progress_planning', 'INTEGER', '0'),
        ('progress_production', 'INTEGER', '0'),
        ('progress_assembly', 'INTEGER', '0'),
        
        # Classification
        ('priority', 'INTEGER', '5'),
        ('complexity', 'VARCHAR(20)', None),
        ('risk_level', 'VARCHAR(20)', None),
        ('strategic_importance', 'VARCHAR(20)', None),
        
        # Contract
        ('contract_type', 'VARCHAR(100)', None),
        ('warranty_months', 'INTEGER', '60'),
        ('retention_percent', 'VARCHAR(10)', None),
        ('retention_amount', 'VARCHAR(20)', None),
        ('performance_bond', 'BOOLEAN', 'false'),
        
        # Quality
        ('quality_requirements', 'TEXT', None),
        ('inspection_plan_required', 'BOOLEAN', 'false'),
        ('acceptance_criteria', 'TEXT', None),
        
        # Communication
        ('communication_channel', 'VARCHAR(50)', None),
        ('report_frequency', 'VARCHAR(50)', None),
        ('next_meeting_date', 'TIMESTAMP', None),
        
        # Reference
        ('is_reference_project', 'BOOLEAN', 'false'),
        ('reference_approved', 'BOOLEAN', 'false'),
        ('photo_permission', 'BOOLEAN', 'false'),
        ('publication_allowed', 'BOOLEAN', 'false'),
        
        # Notes
        ('notes', 'TEXT', None),
        ('internal_notes', 'TEXT', None),
        ('risk_notes', 'TEXT', None),
        
        # Flexible
        ('tags', 'TEXT[]', None),
        ('custom_fields', 'JSONB', None),
        ('extra_metadata', 'JSONB', None),
    ]
    
    added = 0
    for col_name, col_type, default in columns:
        if add_column_if_not_exists(cursor, 'projects', col_name, col_type, default):
            added += 1
    
    print(f"  ✓ Projects: {added} columns added")

def migrate_customers(cursor):
    """Add new columns to customers table"""
    print("\n📋 Migrating customers table...")
    
    columns = [
        ('customer_since', 'DATE', None),
        ('legal_form', 'VARCHAR(50)', None),
        ('industry', 'VARCHAR(100)', None),
        ('employee_count', 'INTEGER', None),
        ('annual_revenue', 'DECIMAL(15,2)', None),
        ('title', 'VARCHAR(30)', None),
        ('position', 'VARCHAR(100)', None),
        ('department', 'VARCHAR(100)', None),
        ('date_of_birth', 'DATE', None),
        ('preferred_language', 'VARCHAR(10)', None),
        ('preferred_contact_method', 'VARCHAR(20)', None),
        ('address_addition', 'VARCHAR(100)', None),
        ('district', 'VARCHAR(100)', None),
        ('country_code', 'VARCHAR(3)', None),
        ('latitude', 'DECIMAL(10,8)', None),
        ('longitude', 'DECIMAL(11,8)', None),
        ('delivery_street', 'VARCHAR(200)', None),
        ('delivery_street_number', 'VARCHAR(20)', None),
        ('delivery_postal_code', 'VARCHAR(20)', None),
        ('delivery_city', 'VARCHAR(100)', None),
        ('delivery_country', 'VARCHAR(100)', None),
        ('invoice_street', 'VARCHAR(200)', None),
        ('invoice_street_number', 'VARCHAR(20)', None),
        ('invoice_postal_code', 'VARCHAR(20)', None),
        ('invoice_city', 'VARCHAR(100)', None),
        ('invoice_country', 'VARCHAR(100)', None),
        ('invoice_email', 'VARCHAR(255)', None),
        ('bank_account_holder', 'VARCHAR(100)', None),
        ('sepa_mandate_id', 'VARCHAR(50)', None),
        ('sepa_mandate_date', 'DATE', None),
        ('vat_id', 'VARCHAR(20)', None),
        ('tax_exempt', 'BOOLEAN', 'false'),
        ('dunning_block', 'BOOLEAN', 'false'),
        ('order_block', 'BOOLEAN', 'false'),
        ('revenue_ytd', 'DECIMAL(15,2)', None),
        ('revenue_last_year', 'DECIMAL(15,2)', None),
        ('revenue_total', 'DECIMAL(15,2)', None),
        ('open_invoices_amount', 'DECIMAL(15,2)', None),
        ('last_order_date', 'DATE', None),
        ('last_invoice_date', 'DATE', None),
        ('last_payment_date', 'DATE', None),
        ('average_payment_days', 'INTEGER', None),
        ('order_count', 'INTEGER', None),
        ('assigned_employee_id', 'UUID', None),
        ('referral_source', 'VARCHAR(100)', None),
        ('referred_by_customer_id', 'UUID', None),
        ('newsletter_subscribed', 'BOOLEAN', 'false'),
        ('marketing_consent', 'BOOLEAN', 'false'),
        ('marketing_consent_date', 'TIMESTAMP', None),
        ('gdpr_consent', 'BOOLEAN', 'false'),
        ('gdpr_consent_date', 'TIMESTAMP', None),
        ('customer_rating', 'INTEGER', None),
        ('risk_rating', 'VARCHAR(20)', None),
        ('documents', 'JSONB', None),
        ('custom_fields', 'JSONB', None),
        ('extra_data', 'JSONB', None),
        ('tags', 'TEXT[]', None),
    ]
    
    added = 0
    for col_name, col_type, default in columns:
        if add_column_if_not_exists(cursor, 'customers', col_name, col_type, default):
            added += 1
    
    print(f"  ✓ Customers: {added} columns added")

def migrate_employees(cursor):
    """Add new columns to employees table"""
    print("\n📋 Migrating employees table...")
    
    columns = [
        ('employee_number', 'VARCHAR(20)', None),
        ('title', 'VARCHAR(30)', None),
        ('date_of_birth', 'DATE', None),
        ('place_of_birth', 'VARCHAR(100)', None),
        ('nationality', 'VARCHAR(50)', None),
        ('gender', 'VARCHAR(20)', None),
        ('marital_status', 'VARCHAR(20)', None),
        ('children_count', 'INTEGER', None),
        ('tax_class', 'VARCHAR(10)', None),
        ('tax_id', 'VARCHAR(20)', None),
        ('social_security_number', 'VARCHAR(30)', None),
        ('health_insurance', 'VARCHAR(100)', None),
        ('health_insurance_number', 'VARCHAR(30)', None),
        ('address_addition', 'VARCHAR(100)', None),
        ('district', 'VARCHAR(100)', None),
        ('state', 'VARCHAR(100)', None),
        ('country_code', 'VARCHAR(3)', None),
        ('emergency_contact_name', 'VARCHAR(100)', None),
        ('emergency_contact_relation', 'VARCHAR(50)', None),
        ('emergency_contact_phone', 'VARCHAR(30)', None),
        ('employment_type', 'VARCHAR(30)', None),
        ('contract_type', 'VARCHAR(30)', None),
        ('hire_date', 'DATE', None),
        ('probation_end_date', 'DATE', None),
        ('contract_end_date', 'DATE', None),
        ('termination_date', 'DATE', None),
        ('termination_reason', 'TEXT', None),
        ('department', 'VARCHAR(100)', None),
        ('cost_center', 'VARCHAR(50)', None),
        ('position', 'VARCHAR(100)', None),
        ('job_title', 'VARCHAR(100)', None),
        ('supervisor_id', 'UUID', None),
        ('work_location', 'VARCHAR(100)', None),
        ('working_hours_per_week', 'DECIMAL(5,2)', None),
        ('working_days_per_week', 'INTEGER', None),
        ('shift_model', 'VARCHAR(50)', None),
        ('time_tracking_required', 'BOOLEAN', 'true'),
        ('base_salary', 'DECIMAL(10,2)', None),
        ('hourly_rate', 'DECIMAL(8,2)', None),
        ('overtime_rate', 'DECIMAL(8,2)', None),
        ('travel_allowance', 'DECIMAL(8,2)', None),
        ('meal_allowance', 'DECIMAL(8,2)', None),
        ('bonus_eligible', 'BOOLEAN', 'false'),
        ('salary_type', 'VARCHAR(20)', None),
        ('payment_method', 'VARCHAR(30)', None),
        ('bank_name', 'VARCHAR(100)', None),
        ('iban', 'VARCHAR(34)', None),
        ('bic', 'VARCHAR(11)', None),
        ('vacation_days_total', 'INTEGER', None),
        ('vacation_days_used', 'INTEGER', None),
        ('vacation_days_remaining', 'INTEGER', None),
        ('sick_days_ytd', 'INTEGER', None),
        ('qualifications', 'TEXT[]', None),
        ('certifications', 'JSONB', None),
        ('skills', 'JSONB', None),
        ('languages', 'JSONB', None),
        ('training_completed', 'JSONB', None),
        ('drivers_license_classes', 'VARCHAR(50)', None),
        ('drivers_license_valid_until', 'DATE', None),
        ('forklift_license', 'BOOLEAN', 'false'),
        ('crane_license', 'VARCHAR(50)', None),
        ('first_aid_trained', 'BOOLEAN', 'false'),
        ('first_aid_valid_until', 'DATE', None),
        ('safety_training_date', 'DATE', None),
        ('safety_training_valid_until', 'DATE', None),
        ('height_work_certified', 'BOOLEAN', 'false'),
        ('work_equipment', 'JSONB', None),
        ('clothing_sizes', 'JSONB', None),
        ('assigned_vehicle_id', 'UUID', None),
        ('photo_url', 'VARCHAR(500)', None),
        ('document_urls', 'JSONB', None),
        ('custom_fields', 'JSONB', None),
        ('extra_data', 'JSONB', None),
        ('tags', 'TEXT[]', None),
    ]
    
    added = 0
    for col_name, col_type, default in columns:
        if add_column_if_not_exists(cursor, 'employees', col_name, col_type, default):
            added += 1
    
    print(f"  ✓ Employees: {added} columns added")

def migrate_invoices(cursor):
    """Add new columns to invoices table"""
    print("\n📋 Migrating invoices table...")
    
    columns = [
        ('invoice_type', 'VARCHAR(30)', None),
        ('is_final_invoice', 'BOOLEAN', 'false'),
        ('partial_invoice_number', 'INTEGER', None),
        ('credit_note_for_invoice_id', 'UUID', None),
        ('cancellation_invoice_id', 'UUID', None),
        ('original_invoice_id', 'UUID', None),
        ('collective_invoice', 'BOOLEAN', 'false'),
        ('invoice_date', 'DATE', None),
        ('service_date_from', 'DATE', None),
        ('service_date_to', 'DATE', None),
        ('delivery_date', 'DATE', None),
        ('due_date', 'DATE', None),
        ('cash_discount_date', 'DATE', None),
        ('cash_discount_percent', 'DECIMAL(5,2)', None),
        ('cash_discount_amount', 'DECIMAL(15,2)', None),
        ('currency', 'VARCHAR(3)', 'EUR'),
        ('exchange_rate', 'DECIMAL(10,6)', '1'),
        ('net_amount', 'DECIMAL(15,2)', None),
        ('discount_amount', 'DECIMAL(15,2)', None),
        ('shipping_cost', 'DECIMAL(15,2)', None),
        ('vat_amount', 'DECIMAL(15,2)', None),
        ('gross_amount', 'DECIMAL(15,2)', None),
        ('retention_amount', 'DECIMAL(15,2)', None),
        ('retention_due_date', 'DATE', None),
        ('retention_released', 'BOOLEAN', 'false'),
        ('paid_amount', 'DECIMAL(15,2)', '0'),
        ('open_amount', 'DECIMAL(15,2)', None),
        ('payment_method', 'VARCHAR(30)', None),
        ('payment_reference', 'VARCHAR(100)', None),
        ('payment_date', 'DATE', None),
        ('bank_account_iban', 'VARCHAR(34)', None),
        ('sepa_mandate_id', 'VARCHAR(50)', None),
        ('billing_name', 'VARCHAR(200)', None),
        ('billing_street', 'VARCHAR(200)', None),
        ('billing_street_number', 'VARCHAR(20)', None),
        ('billing_postal_code', 'VARCHAR(20)', None),
        ('billing_city', 'VARCHAR(100)', None),
        ('billing_country', 'VARCHAR(100)', None),
        ('billing_vat_id', 'VARCHAR(20)', None),
        ('intro_text', 'TEXT', None),
        ('closing_text', 'TEXT', None),
        ('internal_note', 'TEXT', None),
        ('sent_date', 'TIMESTAMP', None),
        ('sent_via', 'VARCHAR(20)', None),
        ('sent_to_email', 'VARCHAR(255)', None),
        ('viewed_date', 'TIMESTAMP', None),
        ('reminder_count', 'INTEGER', '0'),
        ('last_reminder_date', 'DATE', None),
        ('dunning_level', 'INTEGER', '0'),
        ('dunning_block', 'BOOLEAN', 'false'),
        ('dunning_fees', 'DECIMAL(10,2)', None),
        ('written_off', 'BOOLEAN', 'false'),
        ('written_off_date', 'DATE', None),
        ('written_off_reason', 'TEXT', None),
        ('exported', 'BOOLEAN', 'false'),
        ('export_date', 'TIMESTAMP', None),
        ('export_reference', 'VARCHAR(100)', None),
        ('accounting_date', 'DATE', None),
        ('cost_center', 'VARCHAR(50)', None),
        ('profit_center', 'VARCHAR(50)', None),
        ('pdf_url', 'VARCHAR(500)', None),
        ('xml_url', 'VARCHAR(500)', None),
        ('custom_fields', 'JSONB', None),
        ('extra_data', 'JSONB', None),
        ('tags', 'TEXT[]', None),
    ]
    
    added = 0
    for col_name, col_type, default in columns:
        if add_column_if_not_exists(cursor, 'invoices', col_name, col_type, default):
            added += 1
    
    print(f"  ✓ Invoices: {added} columns added")

def migrate_orders(cursor):
    """Add new columns to orders table"""
    print("\n📋 Migrating orders table...")
    
    columns = [
        ('order_type', 'VARCHAR(30)', None),
        ('reference_number', 'VARCHAR(50)', None),
        ('customer_order_number', 'VARCHAR(50)', None),
        ('framework_contract_id', 'UUID', None),
        ('offer_id', 'UUID', None),
        ('order_date', 'DATE', None),
        ('requested_date', 'DATE', None),
        ('confirmed_date', 'DATE', None),
        ('production_start_date', 'DATE', None),
        ('production_end_date', 'DATE', None),
        ('delivery_date', 'DATE', None),
        ('completion_date', 'DATE', None),
        ('currency', 'VARCHAR(3)', 'EUR'),
        ('exchange_rate', 'DECIMAL(10,6)', '1'),
        ('net_amount', 'DECIMAL(15,2)', None),
        ('discount_percent', 'DECIMAL(5,2)', None),
        ('discount_amount', 'DECIMAL(15,2)', None),
        ('shipping_cost', 'DECIMAL(15,2)', None),
        ('vat_amount', 'DECIMAL(15,2)', None),
        ('gross_amount', 'DECIMAL(15,2)', None),
        ('cost_estimate', 'DECIMAL(15,2)', None),
        ('margin_percent', 'DECIMAL(5,2)', None),
        ('payment_terms_days', 'INTEGER', None),
        ('payment_method', 'VARCHAR(30)', None),
        ('delivery_terms', 'VARCHAR(50)', None),
        ('incoterm', 'VARCHAR(20)', None),
        ('shipping_method', 'VARCHAR(50)', None),
        ('delivery_street', 'VARCHAR(200)', None),
        ('delivery_street_number', 'VARCHAR(20)', None),
        ('delivery_postal_code', 'VARCHAR(20)', None),
        ('delivery_city', 'VARCHAR(100)', None),
        ('delivery_country', 'VARCHAR(100)', None),
        ('delivery_contact_name', 'VARCHAR(100)', None),
        ('delivery_contact_phone', 'VARCHAR(30)', None),
        ('delivery_instructions', 'TEXT', None),
        ('priority', 'VARCHAR(20)', 'NORMAL'),
        ('production_status', 'VARCHAR(30)', None),
        ('assigned_team', 'VARCHAR(100)', None),
        ('intro_text', 'TEXT', None),
        ('closing_text', 'TEXT', None),
        ('internal_note', 'TEXT', None),
        ('customer_note', 'TEXT', None),
        ('terms_accepted', 'BOOLEAN', 'false'),
        ('terms_accepted_date', 'TIMESTAMP', None),
        ('sent_date', 'TIMESTAMP', None),
        ('confirmed_by', 'VARCHAR(100)', None),
        ('custom_fields', 'JSONB', None),
        ('extra_data', 'JSONB', None),
        ('tags', 'TEXT[]', None),
    ]
    
    added = 0
    for col_name, col_type, default in columns:
        if add_column_if_not_exists(cursor, 'orders', col_name, col_type, default):
            added += 1
    
    print(f"  ✓ Orders: {added} columns added")

def migrate_inventory(cursor):
    """Add new columns to inventory tables"""
    print("\n📋 Migrating inventory tables...")
    
    # Check if articles table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'articles'
        )
    """)
    if not cursor.fetchone()[0]:
        print("  ⚠ Articles table does not exist, skipping")
        return
    
    # Articles table
    article_columns = [
        ('article_group', 'VARCHAR(100)', None),
        ('article_category', 'VARCHAR(100)', None),
        ('article_subcategory', 'VARCHAR(100)', None),
        ('manufacturer', 'VARCHAR(100)', None),
        ('manufacturer_number', 'VARCHAR(50)', None),
        ('brand', 'VARCHAR(100)', None),
        ('ean_code', 'VARCHAR(20)', None),
        ('customs_tariff_number', 'VARCHAR(20)', None),
        ('country_of_origin', 'VARCHAR(50)', None),
        ('weight_kg', 'DECIMAL(10,3)', None),
        ('length_mm', 'DECIMAL(10,2)', None),
        ('width_mm', 'DECIMAL(10,2)', None),
        ('height_mm', 'DECIMAL(10,2)', None),
        ('volume_cbm', 'DECIMAL(10,4)', None),
        ('base_unit', 'VARCHAR(20)', None),
        ('sales_unit', 'VARCHAR(20)', None),
        ('purchase_unit', 'VARCHAR(20)', None),
        ('conversion_factor', 'DECIMAL(10,4)', '1'),
        ('min_order_quantity', 'DECIMAL(10,2)', None),
        ('order_increment', 'DECIMAL(10,2)', None),
        ('lead_time_days', 'INTEGER', None),
        ('safety_stock', 'DECIMAL(10,2)', None),
        ('reorder_point', 'DECIMAL(10,2)', None),
        ('reorder_quantity', 'DECIMAL(10,2)', None),
        ('max_stock', 'DECIMAL(10,2)', None),
        ('purchase_price', 'DECIMAL(15,4)', None),
        ('last_purchase_price', 'DECIMAL(15,4)', None),
        ('average_purchase_price', 'DECIMAL(15,4)', None),
        ('list_price', 'DECIMAL(15,4)', None),
        ('sales_price', 'DECIMAL(15,4)', None),
        ('min_sales_price', 'DECIMAL(15,4)', None),
        ('margin_percent', 'DECIMAL(5,2)', None),
        ('discount_group', 'VARCHAR(50)', None),
        ('price_group', 'VARCHAR(50)', None),
        ('vat_rate', 'DECIMAL(5,2)', '19.00'),
        ('serial_number_required', 'BOOLEAN', 'false'),
        ('batch_required', 'BOOLEAN', 'false'),
        ('expiry_tracking', 'BOOLEAN', 'false'),
        ('hazardous_material', 'BOOLEAN', 'false'),
        ('hazard_class', 'VARCHAR(50)', None),
        ('storage_conditions', 'TEXT', None),
        ('handling_instructions', 'TEXT', None),
        ('certifications', 'TEXT[]', None),
        ('wood_type', 'VARCHAR(50)', None),
        ('wood_quality', 'VARCHAR(30)', None),
        ('wood_moisture_percent', 'DECIMAL(5,2)', None),
        ('wood_certification', 'VARCHAR(50)', None),
        ('sustainability_info', 'TEXT', None),
        ('image_urls', 'JSONB', None),
        ('document_urls', 'JSONB', None),
        ('technical_data', 'JSONB', None),
        ('custom_fields', 'JSONB', None),
        ('extra_data', 'JSONB', None),
        ('tags', 'TEXT[]', None),
    ]
    
    added = 0
    for col_name, col_type, default in article_columns:
        if add_column_if_not_exists(cursor, 'articles', col_name, col_type, default):
            added += 1
    
    print(f"  ✓ Articles: {added} columns added")

def migrate_materials(cursor):
    """Add new columns to materials table - COMPLETE SCHEMA"""
    print("\n📋 Migrating materials table...")
    
    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'materials'
        )
    """)
    if not cursor.fetchone()[0]:
        print("  ⚠ Materials table does not exist - will be created by SQLAlchemy")
        return
    
    # ALL columns from inventory.py Material model
    columns = [
        # Identifiers
        ('gtin', 'VARCHAR(20)', None),
        ('manufacturer_number', 'VARCHAR(100)', None),
        ('name_short', 'VARCHAR(100)', None),
        ('description_long', 'TEXT', None),
        
        # Category
        ('subcategory', 'VARCHAR(100)', None),
        ('product_group', 'VARCHAR(100)', None),
        ('product_line', 'VARCHAR(100)', None),
        
        # Manufacturer
        ('manufacturer', 'VARCHAR(255)', None),
        ('brand', 'VARCHAR(100)', None),
        ('manufacturer_url', 'VARCHAR(500)', None),
        
        # Dimensions
        ('length_mm', 'INTEGER', None),
        ('width_mm', 'INTEGER', None),
        ('height_mm', 'INTEGER', None),
        ('length_tolerance_mm', 'VARCHAR(20)', None),
        ('width_tolerance_mm', 'VARCHAR(20)', None),
        ('height_tolerance_mm', 'VARCHAR(20)', None),
        ('diameter_mm', 'INTEGER', None),
        ('thread_size', 'VARCHAR(20)', None),
        ('weight_kg', 'VARCHAR(20)', None),
        ('weight_per_meter', 'VARCHAR(20)', None),
        ('weight_per_sqm', 'VARCHAR(20)', None),
        ('volume_m3', 'VARCHAR(20)', None),
        
        # Units
        ('base_unit', 'VARCHAR(20)', None),
        ('sales_unit', 'VARCHAR(20)', None),
        ('purchase_unit', 'VARCHAR(20)', None),
        ('unit_conversion', 'JSONB', '{}'),
        ('packaging_unit', 'VARCHAR(50)', None),
        ('pieces_per_package', 'INTEGER', None),
        ('packages_per_pallet', 'INTEGER', None),
        ('pallet_quantity', 'INTEGER', None),
        
        # Wood-specific
        ('wood_type', 'VARCHAR(100)', None),
        ('wood_type_latin', 'VARCHAR(100)', None),
        ('wood_origin', 'VARCHAR(100)', None),
        ('quality_grade', 'VARCHAR(50)', None),
        ('strength_class', 'VARCHAR(20)', None),
        ('appearance_class', 'VARCHAR(20)', None),
        ('moisture_content', 'VARCHAR(10)', None),
        ('moisture_content_min', 'VARCHAR(10)', None),
        ('moisture_content_max', 'VARCHAR(10)', None),
        ('treatment', 'VARCHAR(100)', None),
        ('surface_treatment', 'VARCHAR(100)', None),
        ('impregnation', 'VARCHAR(100)', None),
        ('fire_protection_class', 'VARCHAR(20)', None),
        ('certification', 'VARCHAR(50)', None),
        ('certification_number', 'VARCHAR(100)', None),
        ('ce_marking', 'BOOLEAN', 'false'),
        ('declaration_of_performance', 'VARCHAR(100)', None),
        
        # Technical values
        ('density_kg_m3', 'VARCHAR(20)', None),
        ('bending_strength_mpa', 'VARCHAR(20)', None),
        ('tensile_strength_mpa', 'VARCHAR(20)', None),
        ('compression_strength_mpa', 'VARCHAR(20)', None),
        ('shear_strength_mpa', 'VARCHAR(20)', None),
        ('e_modulus_mpa', 'VARCHAR(20)', None),
        ('thermal_conductivity', 'VARCHAR(20)', None),
        ('vapor_diffusion_resistance', 'VARCHAR(20)', None),
        ('fire_reaction_class', 'VARCHAR(20)', None),
        ('sound_insulation_rw', 'VARCHAR(20)', None),
        
        # Fastener-specific
        ('head_type', 'VARCHAR(50)', None),
        ('drive_type', 'VARCHAR(50)', None),
        ('tip_type', 'VARCHAR(50)', None),
        ('thread_type', 'VARCHAR(50)', None),
        ('material_type', 'VARCHAR(100)', None),
        ('coating', 'VARCHAR(100)', None),
        ('corrosion_class', 'VARCHAR(20)', None),
        ('eta_number', 'VARCHAR(100)', None),
        ('approval_document', 'VARCHAR(255)', None),
        ('characteristic_load_capacity', 'VARCHAR(100)', None),
        
        # Prices
        ('purchase_price', 'VARCHAR(20)', None),
        ('purchase_price_date', 'DATE', None),
        ('list_price', 'VARCHAR(20)', None),
        ('selling_price', 'VARCHAR(20)', None),
        ('minimum_price', 'VARCHAR(20)', None),
        ('margin_percent', 'VARCHAR(10)', None),
        ('markup_percent', 'VARCHAR(10)', None),
        ('tax_rate', 'VARCHAR(10)', '19'),
        ('price_scales', 'JSONB', '[]'),
        
        # Stock
        ('min_stock', 'VARCHAR(20)', '0'),
        ('max_stock', 'VARCHAR(20)', None),
        ('safety_stock', 'VARCHAR(20)', None),
        ('reorder_point', 'VARCHAR(20)', None),
        ('reorder_quantity', 'VARCHAR(20)', None),
        ('lot_size', 'VARCHAR(20)', None),
        ('current_stock', 'VARCHAR(20)', '0'),
        ('reserved_stock', 'VARCHAR(20)', '0'),
        ('available_stock', 'VARCHAR(20)', '0'),
        ('ordered_stock', 'VARCHAR(20)', '0'),
        ('average_consumption', 'VARCHAR(20)', None),
        ('last_purchase_date', 'DATE', None),
        ('last_sale_date', 'DATE', None),
        ('turnover_rate', 'VARCHAR(10)', None),
        
        # Supplier
        ('primary_supplier_id', 'UUID', None),
        ('supplier_article_number', 'VARCHAR(100)', None),
        ('lead_time_days', 'INTEGER', None),
        ('minimum_order_quantity', 'VARCHAR(20)', None),
        
        # Storage
        ('default_location_id', 'UUID', None),
        ('storage_conditions', 'TEXT', None),
        ('shelf_life_days', 'INTEGER', None),
        
        # Flags
        ('is_active', 'BOOLEAN', 'true'),
        ('is_producible', 'BOOLEAN', 'false'),
        ('is_purchasable', 'BOOLEAN', 'true'),
        ('is_sellable', 'BOOLEAN', 'true'),
        ('is_stockable', 'BOOLEAN', 'true'),
        ('is_serial_tracked', 'BOOLEAN', 'false'),
        ('is_batch_tracked', 'BOOLEAN', 'false'),
        ('is_hazardous', 'BOOLEAN', 'false'),
        ('status', 'VARCHAR(50)', 'active'),
        ('discontinued_date', 'DATE', None),
        ('replacement_article_id', 'UUID', None),
        
        # Documents
        ('image_url', 'VARCHAR(500)', None),
        ('image_urls', 'JSONB', '[]'),
        ('datasheet_url', 'VARCHAR(500)', None),
        ('safety_datasheet_url', 'VARCHAR(500)', None),
        ('installation_guide_url', 'VARCHAR(500)', None),
        ('video_url', 'VARCHAR(500)', None),
        
        # Notes
        ('notes', 'TEXT', None),
        ('internal_notes', 'TEXT', None),
        ('purchase_notes', 'TEXT', None),
        ('production_notes', 'TEXT', None),
        
        # Flexible
        ('tags', 'TEXT[]', None),
        ('custom_fields', 'JSONB', '{}'),
        ('technical_data', 'JSONB', '{}'),
    ]
    
    added = 0
    for col_name, col_type, default in columns:
        if add_column_if_not_exists(cursor, 'materials', col_name, col_type, default):
            added += 1
    
    print(f"  ✓ Materials: {added} columns added")


def create_new_tables(cursor):
    """Create new tables for extended functionality"""
    print("\n📋 Creating new tables...")
    
    # Construction diary entries
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS construction_diary_entries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            project_id UUID NOT NULL REFERENCES projects(id),
            entry_date DATE NOT NULL,
            weather_morning VARCHAR(50),
            weather_morning_temp DECIMAL(4,1),
            weather_noon VARCHAR(50),
            weather_noon_temp DECIMAL(4,1),
            weather_evening VARCHAR(50),
            weather_evening_temp DECIMAL(4,1),
            precipitation_mm DECIMAL(6,2),
            wind_speed_kmh DECIMAL(5,1),
            work_possible BOOLEAN DEFAULT true,
            work_interruption_hours DECIMAL(4,2),
            interruption_reason TEXT,
            employees_on_site INTEGER,
            subcontractor_workers INTEGER,
            work_description TEXT,
            progress_notes TEXT,
            materials_used JSONB,
            deliveries JSONB,
            visitors JSONB,
            meetings JSONB,
            incidents JSONB,
            safety_observations TEXT,
            quality_notes TEXT,
            photos JSONB,
            signature_site_manager TEXT,
            signature_client TEXT,
            signed_at TIMESTAMP,
            created_by UUID,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  + Created construction_diary_entries table")
    
    # Vehicles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            vehicle_number VARCHAR(20),
            license_plate VARCHAR(20),
            vehicle_type VARCHAR(50),
            brand VARCHAR(50),
            model VARCHAR(100),
            year INTEGER,
            vin VARCHAR(50),
            color VARCHAR(30),
            fuel_type VARCHAR(30),
            engine_power_kw INTEGER,
            max_weight_kg INTEGER,
            payload_kg INTEGER,
            mileage_km INTEGER,
            operating_hours DECIMAL(10,2),
            purchase_date DATE,
            purchase_price DECIMAL(15,2),
            current_value DECIMAL(15,2),
            tuv_valid_until DATE,
            au_valid_until DATE,
            uvv_valid_until DATE,
            next_service_date DATE,
            next_service_km INTEGER,
            insurance_company VARCHAR(100),
            insurance_number VARCHAR(50),
            insurance_valid_until DATE,
            gps_device_id VARCHAR(50),
            gps_enabled BOOLEAN DEFAULT false,
            current_latitude DECIMAL(10,8),
            current_longitude DECIMAL(11,8),
            current_location_updated TIMESTAMP,
            assigned_employee_id UUID REFERENCES employees(id),
            assigned_project_id UUID REFERENCES projects(id),
            status VARCHAR(30) DEFAULT 'AVAILABLE',
            notes TEXT,
            documents JSONB,
            custom_fields JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false,
            deleted_at TIMESTAMP
        )
    """)
    print("  + Created vehicles table")
    
    # Fuel logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuel_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            vehicle_id UUID NOT NULL REFERENCES vehicles(id),
            log_date TIMESTAMP NOT NULL,
            fuel_type VARCHAR(30),
            quantity_liters DECIMAL(8,2),
            price_per_liter DECIMAL(6,3),
            total_cost DECIMAL(10,2),
            mileage_km INTEGER,
            station_name VARCHAR(100),
            station_location VARCHAR(200),
            receipt_number VARCHAR(50),
            driver_id UUID REFERENCES employees(id),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  + Created fuel_logs table")
    
    # Trip logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trip_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            vehicle_id UUID NOT NULL REFERENCES vehicles(id),
            driver_id UUID REFERENCES employees(id),
            trip_date DATE NOT NULL,
            start_time TIME,
            end_time TIME,
            start_mileage INTEGER,
            end_mileage INTEGER,
            distance_km INTEGER,
            start_location VARCHAR(200),
            end_location VARCHAR(200),
            via_locations TEXT,
            trip_purpose VARCHAR(50),
            trip_type VARCHAR(30),
            project_id UUID REFERENCES projects(id),
            customer_id UUID REFERENCES customers(id),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  + Created trip_logs table")
    
    # Equipment
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            equipment_number VARCHAR(20),
            name VARCHAR(100) NOT NULL,
            equipment_type VARCHAR(50),
            category VARCHAR(50),
            brand VARCHAR(50),
            model VARCHAR(100),
            serial_number VARCHAR(50),
            year INTEGER,
            purchase_date DATE,
            purchase_price DECIMAL(15,2),
            current_value DECIMAL(15,2),
            rental_price_day DECIMAL(10,2),
            operating_hours DECIMAL(10,2),
            next_service_hours DECIMAL(10,2),
            next_service_date DATE,
            uvv_valid_until DATE,
            calibration_valid_until DATE,
            power_type VARCHAR(30),
            power_consumption VARCHAR(50),
            weight_kg DECIMAL(10,2),
            dimensions VARCHAR(100),
            lift_capacity_kg DECIMAL(10,2),
            reach_m DECIMAL(6,2),
            current_location VARCHAR(200),
            assigned_project_id UUID REFERENCES projects(id),
            assigned_employee_id UUID REFERENCES employees(id),
            status VARCHAR(30) DEFAULT 'AVAILABLE',
            condition_rating INTEGER,
            notes TEXT,
            documents JSONB,
            maintenance_history JSONB,
            custom_fields JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false,
            deleted_at TIMESTAMP
        )
    """)
    print("  + Created equipment table")
    
    # Activities (CRM)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            activity_type VARCHAR(30) NOT NULL,
            subject VARCHAR(200) NOT NULL,
            description TEXT,
            status VARCHAR(30) DEFAULT 'PLANNED',
            priority VARCHAR(20) DEFAULT 'NORMAL',
            due_date TIMESTAMP,
            completed_date TIMESTAMP,
            duration_minutes INTEGER,
            customer_id UUID REFERENCES customers(id),
            contact_name VARCHAR(100),
            contact_email VARCHAR(255),
            contact_phone VARCHAR(30),
            project_id UUID REFERENCES projects(id),
            lead_id UUID,
            opportunity_id UUID,
            assigned_to UUID REFERENCES employees(id),
            location VARCHAR(200),
            meeting_type VARCHAR(30),
            call_direction VARCHAR(20),
            call_result VARCHAR(50),
            email_subject VARCHAR(200),
            email_sent BOOLEAN DEFAULT false,
            reminder_date TIMESTAMP,
            reminder_sent BOOLEAN DEFAULT false,
            is_recurring BOOLEAN DEFAULT false,
            recurrence_pattern VARCHAR(50),
            recurrence_end_date DATE,
            parent_activity_id UUID,
            outcome TEXT,
            next_steps TEXT,
            attachments JSONB,
            custom_fields JSONB,
            created_by UUID,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false,
            deleted_at TIMESTAMP
        )
    """)
    print("  + Created activities table")
    
    # Leads
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            lead_number VARCHAR(20),
            status VARCHAR(30) DEFAULT 'NEW',
            source VARCHAR(50),
            source_detail VARCHAR(200),
            campaign_id UUID,
            company_name VARCHAR(200),
            industry VARCHAR(100),
            employee_count INTEGER,
            annual_revenue DECIMAL(15,2),
            salutation VARCHAR(20),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            title VARCHAR(50),
            position VARCHAR(100),
            email VARCHAR(255),
            phone VARCHAR(30),
            mobile VARCHAR(30),
            website VARCHAR(255),
            street VARCHAR(200),
            street_number VARCHAR(20),
            postal_code VARCHAR(20),
            city VARCHAR(100),
            country VARCHAR(100),
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            interest_areas TEXT[],
            project_type VARCHAR(50),
            project_description TEXT,
            budget_range VARCHAR(50),
            estimated_value DECIMAL(15,2),
            expected_close_date DATE,
            decision_timeframe VARCHAR(50),
            decision_maker BOOLEAN DEFAULT false,
            competitors TEXT[],
            lead_score INTEGER DEFAULT 0,
            rating VARCHAR(20),
            assigned_to UUID REFERENCES employees(id),
            last_contact_date TIMESTAMP,
            next_follow_up_date DATE,
            converted_to_customer_id UUID REFERENCES customers(id),
            converted_to_opportunity_id UUID,
            converted_date TIMESTAMP,
            conversion_notes TEXT,
            lost_reason VARCHAR(100),
            lost_date DATE,
            notes TEXT,
            custom_fields JSONB,
            created_by UUID,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false,
            deleted_at TIMESTAMP
        )
    """)
    print("  + Created leads table")
    
    # Quality inspections
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quality_inspections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            inspection_number VARCHAR(20),
            inspection_type VARCHAR(50) NOT NULL,
            status VARCHAR(30) DEFAULT 'PLANNED',
            project_id UUID REFERENCES projects(id),
            order_id UUID,
            article_id UUID,
            inspection_date TIMESTAMP,
            planned_date DATE,
            inspector_id UUID REFERENCES employees(id),
            inspector_name VARCHAR(100),
            location VARCHAR(200),
            checklist_template_id UUID,
            checklist_items JSONB,
            measurements JSONB,
            overall_result VARCHAR(30),
            pass_count INTEGER,
            fail_count INTEGER,
            total_checks INTEGER,
            defects_found JSONB,
            corrective_actions TEXT,
            photos JSONB,
            documents JSONB,
            client_present BOOLEAN DEFAULT false,
            client_signature TEXT,
            inspector_signature TEXT,
            signed_at TIMESTAMP,
            follow_up_required BOOLEAN DEFAULT false,
            follow_up_date DATE,
            notes TEXT,
            custom_fields JSONB,
            created_by UUID,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false,
            deleted_at TIMESTAMP
        )
    """)
    print("  + Created quality_inspections table")
    
    # Defects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS defects (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            defect_number VARCHAR(20),
            status VARCHAR(30) DEFAULT 'OPEN',
            severity VARCHAR(20) DEFAULT 'MEDIUM',
            project_id UUID REFERENCES projects(id),
            inspection_id UUID REFERENCES quality_inspections(id),
            location_description TEXT,
            defect_type VARCHAR(50),
            defect_category VARCHAR(50),
            description TEXT NOT NULL,
            cause_analysis TEXT,
            reported_date DATE NOT NULL,
            reported_by VARCHAR(100),
            responsible_party VARCHAR(100),
            assigned_to UUID REFERENCES employees(id),
            due_date DATE,
            completion_date DATE,
            corrective_action TEXT,
            preventive_action TEXT,
            cost_estimate DECIMAL(15,2),
            actual_cost DECIMAL(15,2),
            cost_responsibility VARCHAR(50),
            warranty_claim BOOLEAN DEFAULT false,
            warranty_claim_number VARCHAR(50),
            photos_before JSONB,
            photos_after JSONB,
            documents JSONB,
            customer_notified BOOLEAN DEFAULT false,
            customer_accepted BOOLEAN,
            acceptance_date DATE,
            notes TEXT,
            custom_fields JSONB,
            created_by UUID,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false,
            deleted_at TIMESTAMP
        )
    """)
    print("  + Created defects table")
    
    # Certificates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            certificate_number VARCHAR(50),
            certificate_type VARCHAR(50) NOT NULL,
            name VARCHAR(200) NOT NULL,
            issuing_authority VARCHAR(200),
            project_id UUID REFERENCES projects(id),
            article_id UUID,
            employee_id UUID REFERENCES employees(id),
            issue_date DATE,
            valid_from DATE,
            valid_until DATE,
            status VARCHAR(30) DEFAULT 'VALID',
            scope TEXT,
            standard_reference VARCHAR(100),
            verification_url VARCHAR(500),
            document_url VARCHAR(500),
            notes TEXT,
            custom_fields JSONB,
            created_by UUID,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false,
            deleted_at TIMESTAMP
        )
    """)
    print("  + Created certificates table")

def migrate_bank_accounts(cursor):
    """Add new columns to bank_accounts table"""
    print("\n📋 Migrating bank_accounts table...")
    
    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'bank_accounts'
        )
    """)
    if not cursor.fetchone()[0]:
        print("  ⚠ bank_accounts table does not exist - will be created by SQLAlchemy")
        return
    
    columns = [
        ('provider', 'VARCHAR(50)', 'manual'),
        ('credentials_encrypted', 'TEXT', None),
        ('balance', 'DECIMAL(15,2)', '0'),
    ]
    
    added = 0
    for col_name, col_type, default in columns:
        if add_column_if_not_exists(cursor, 'bank_accounts', col_name, col_type, default):
            added += 1
    
    print(f"  ✓ Bank Accounts: {added} columns added")


def create_telemetry_tables(cursor):
    """Create telemetry tables"""
    print("\n📋 Creating telemetry tables...")
    
    # Telemetry Events
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            event_id VARCHAR(100) NOT NULL,
            event_name VARCHAR(255) NOT NULL,
            event_version VARCHAR(20) DEFAULT '1.0',
            category VARCHAR(30) DEFAULT 'system',
            severity VARCHAR(20) DEFAULT 'info',
            tags TEXT[],
            event_data JSONB DEFAULT '{}',
            event_context JSONB DEFAULT '{}',
            event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            source_module VARCHAR(100),
            source_function VARCHAR(255),
            source_file VARCHAR(500),
            source_line INTEGER,
            user_id UUID REFERENCES users(id),
            session_id VARCHAR(100),
            client_ip INET,
            client_user_agent TEXT,
            client_version VARCHAR(50),
            client_platform VARCHAR(50),
            correlation_id VARCHAR(100),
            parent_event_id UUID,
            trace_id VARCHAR(100),
            span_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_telemetry_events_timestamp ON telemetry_events(event_timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_telemetry_events_category ON telemetry_events(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_telemetry_events_user ON telemetry_events(user_id)")
    print("  + Created telemetry_events table")
    
    # System Metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            metric_name VARCHAR(255) NOT NULL,
            metric_type VARCHAR(30) DEFAULT 'gauge',
            metric_unit VARCHAR(50),
            value FLOAT NOT NULL,
            min_value FLOAT,
            max_value FLOAT,
            avg_value FLOAT,
            sum_value FLOAT,
            count INTEGER DEFAULT 1,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            period_start TIMESTAMP,
            period_end TIMESTAMP,
            aggregation_interval VARCHAR(20),
            labels JSONB DEFAULT '{}',
            host VARCHAR(255),
            service VARCHAR(100),
            instance VARCHAR(100),
            warning_threshold FLOAT,
            critical_threshold FLOAT,
            is_anomaly BOOLEAN DEFAULT false,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_system_metrics_name ON system_metrics(metric_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_system_metrics_timestamp ON system_metrics(timestamp)")
    print("  + Created system_metrics table")
    
    # Performance Traces
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_traces (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            trace_id VARCHAR(100) NOT NULL,
            span_id VARCHAR(100) NOT NULL,
            parent_span_id VARCHAR(100),
            operation_name VARCHAR(255) NOT NULL,
            operation_type VARCHAR(50),
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            duration_ms FLOAT,
            status_code VARCHAR(20),
            is_error BOOLEAN DEFAULT false,
            error_message TEXT,
            user_id UUID REFERENCES users(id),
            session_id VARCHAR(100),
            request_data JSONB DEFAULT '{}',
            response_data JSONB DEFAULT '{}',
            metadata_info JSONB DEFAULT '{}',
            tags TEXT[],
            cpu_time_ms FLOAT,
            memory_used_bytes INTEGER,
            db_queries_count INTEGER DEFAULT 0,
            db_time_ms FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_performance_traces_trace ON performance_traces(trace_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_performance_traces_duration ON performance_traces(duration_ms)")
    print("  + Created performance_traces table")
    
    # Error Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            error_hash VARCHAR(64) NOT NULL,
            error_type VARCHAR(255) NOT NULL,
            error_message TEXT NOT NULL,
            stack_trace TEXT,
            stack_frames JSONB DEFAULT '[]',
            module VARCHAR(255),
            function VARCHAR(255),
            file_path VARCHAR(500),
            line_number INTEGER,
            user_id UUID REFERENCES users(id),
            session_id VARCHAR(100),
            request_url VARCHAR(2000),
            request_method VARCHAR(10),
            request_params JSONB DEFAULT '{}',
            request_headers JSONB DEFAULT '{}',
            environment VARCHAR(50) DEFAULT 'production',
            app_version VARCHAR(50),
            python_version VARCHAR(20),
            os_info VARCHAR(100),
            severity VARCHAR(20) DEFAULT 'error',
            is_handled BOOLEAN DEFAULT false,
            is_resolved BOOLEAN DEFAULT false,
            resolved_at TIMESTAMP,
            resolved_by UUID REFERENCES users(id),
            extra_data JSONB DEFAULT '{}',
            tags TEXT[],
            occurrence_count INTEGER DEFAULT 1,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_error_logs_hash ON error_logs(error_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_error_logs_type ON error_logs(error_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_error_logs_resolved ON error_logs(is_resolved)")
    print("  + Created error_logs table")
    
    # User Sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            user_id UUID NOT NULL REFERENCES users(id),
            session_token VARCHAR(255) NOT NULL UNIQUE,
            session_hash VARCHAR(64),
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT true,
            end_reason VARCHAR(50),
            client_ip INET,
            client_user_agent TEXT,
            client_device_type VARCHAR(50),
            client_os VARCHAR(100),
            client_browser VARCHAR(100),
            client_version VARCHAR(50),
            geo_country VARCHAR(100),
            geo_city VARCHAR(100),
            geo_latitude FLOAT,
            geo_longitude FLOAT,
            page_views INTEGER DEFAULT 0,
            actions_count INTEGER DEFAULT 0,
            total_duration_seconds INTEGER DEFAULT 0,
            is_suspicious BOOLEAN DEFAULT false,
            security_flags TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_sessions_token ON user_sessions(session_token)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_sessions_user ON user_sessions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_sessions_active ON user_sessions(is_active)")
    print("  + Created user_sessions table")
    
    # User Activities
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activities (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            user_id UUID NOT NULL REFERENCES users(id),
            session_id UUID REFERENCES user_sessions(id),
            activity_type VARCHAR(50) NOT NULL,
            activity_name VARCHAR(255) NOT NULL,
            activity_description TEXT,
            module VARCHAR(100),
            view VARCHAR(100),
            component VARCHAR(100),
            target_entity_type VARCHAR(100),
            target_entity_id UUID,
            target_entity_name VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_ms INTEGER,
            activity_data JSONB DEFAULT '{}',
            previous_state JSONB,
            new_state JSONB,
            was_successful BOOLEAN DEFAULT true,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_activities_user ON user_activities(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_activities_type ON user_activities(activity_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_activities_timestamp ON user_activities(timestamp)")
    print("  + Created user_activities table")
    
    # Audit Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            user_id UUID REFERENCES users(id),
            user_email VARCHAR(255),
            user_name VARCHAR(255),
            user_role VARCHAR(100),
            action VARCHAR(50) NOT NULL,
            action_category VARCHAR(50),
            action_description TEXT,
            resource_type VARCHAR(100) NOT NULL,
            resource_id VARCHAR(100),
            resource_name VARCHAR(255),
            old_values JSONB,
            new_values JSONB,
            changed_fields TEXT[],
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address INET,
            user_agent TEXT,
            session_id VARCHAR(100),
            is_sensitive BOOLEAN DEFAULT false,
            requires_retention BOOLEAN DEFAULT true,
            retention_until DATE,
            checksum VARCHAR(64),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_user ON audit_logs(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs(action)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_resource ON audit_logs(resource_type, resource_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs(timestamp)")
    print("  + Created audit_logs table")
    
    # Feature Usage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feature_usage (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            feature_name VARCHAR(255) NOT NULL,
            feature_category VARCHAR(100),
            feature_version VARCHAR(20),
            date DATE NOT NULL,
            usage_count INTEGER DEFAULT 0,
            unique_users INTEGER DEFAULT 0,
            total_duration_ms INTEGER DEFAULT 0,
            avg_duration_ms FLOAT,
            success_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            success_rate FLOAT,
            additional_metrics JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_feature_usage_feature ON feature_usage(feature_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_feature_usage_date ON feature_usage(date)")
    print("  + Created feature_usage table")
    
    # System Health
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_health (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            check_name VARCHAR(255) NOT NULL,
            check_type VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) NOT NULL,
            is_healthy BOOLEAN DEFAULT true,
            response_time_ms FLOAT,
            latency_p50_ms FLOAT,
            latency_p95_ms FLOAT,
            latency_p99_ms FLOAT,
            cpu_percent FLOAT,
            memory_percent FLOAT,
            disk_percent FLOAT,
            details JSONB DEFAULT '{}',
            error_message TEXT,
            uptime_seconds INTEGER,
            last_downtime TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_system_health_check ON system_health(check_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_system_health_timestamp ON system_health(timestamp)")
    print("  + Created system_health table")
    
    # Alerts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            alert_name VARCHAR(255) NOT NULL,
            alert_type VARCHAR(50) NOT NULL,
            severity VARCHAR(20) DEFAULT 'warning',
            trigger_condition TEXT,
            trigger_value FLOAT,
            threshold_value FLOAT,
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged_at TIMESTAMP,
            acknowledged_by UUID REFERENCES users(id),
            resolved_at TIMESTAMP,
            resolved_by UUID REFERENCES users(id),
            is_active BOOLEAN DEFAULT true,
            is_acknowledged BOOLEAN DEFAULT false,
            is_resolved BOOLEAN DEFAULT false,
            notification_sent BOOLEAN DEFAULT false,
            notification_channels TEXT[],
            source_metric VARCHAR(255),
            source_service VARCHAR(100),
            related_entity_type VARCHAR(100),
            related_entity_id UUID,
            message TEXT,
            details JSONB DEFAULT '{}',
            resolution_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_alerts_active ON alerts(is_active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_alerts_severity ON alerts(severity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_alerts_triggered ON alerts(triggered_at)")
    print("  + Created alerts table")
    
    # Report Schedules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_schedules (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            report_name VARCHAR(255) NOT NULL,
            report_type VARCHAR(50) NOT NULL,
            report_format VARCHAR(20) DEFAULT 'pdf',
            is_active BOOLEAN DEFAULT true,
            schedule_cron VARCHAR(100),
            next_run_at TIMESTAMP,
            last_run_at TIMESTAMP,
            recipients TEXT[],
            report_parameters JSONB DEFAULT '{}',
            date_range_type VARCHAR(50) DEFAULT 'last_7_days',
            created_by UUID REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  + Created report_schedules table")

def main():
    print("=" * 60)
    print("HolzbauERP Database Migration")
    print("=" * 60)
    
    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("\n✓ Connected to database")
        
        # Run migrations
        migrate_tenants(cursor)
        migrate_projects(cursor)
        migrate_customers(cursor)
        migrate_employees(cursor)
        migrate_invoices(cursor)
        migrate_orders(cursor)
        migrate_inventory(cursor)
        migrate_materials(cursor)
        migrate_bank_accounts(cursor)
        create_new_tables(cursor)
        create_telemetry_tables(cursor)
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
