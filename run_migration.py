"""
Vollständige Datenbank-Migration für HolzbauERP
Fügt alle fehlenden Tabellen und Spalten hinzu
"""
import psycopg2
from psycopg2 import sql
import ssl

# Datenbankverbindung
DB_CONFIG = {
    'host': 'public-master-zmbdbeybepes.db.upclouddatabases.com',
    'port': 11569,
    'user': 'upadmin',
    'password': 'AVNS_j5p8EGB21QxeE1u-Fc3',
    'database': 'defaultdb',
    'sslmode': 'require'
}

def get_connection():
    """Erstellt eine Datenbankverbindung"""
    return psycopg2.connect(**DB_CONFIG)

def column_exists(cursor, table_name, column_name):
    """Prüft ob eine Spalte existiert"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        )
    """, (table_name, column_name))
    return cursor.fetchone()[0]

def table_exists(cursor, table_name):
    """Prüft ob eine Tabelle existiert"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = %s
        )
    """, (table_name,))
    return cursor.fetchone()[0]

def add_column_if_not_exists(cursor, table_name, column_name, column_type, default=None):
    """Fügt eine Spalte hinzu, falls sie nicht existiert"""
    if not column_exists(cursor, table_name, column_name):
        try:
            if default is not None:
                cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT %s', (default,))
            else:
                cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}')
            print(f"  ✓ Spalte {column_name} zu {table_name} hinzugefügt")
            return True
        except Exception as e:
            print(f"  ✗ Fehler bei {table_name}.{column_name}: {e}")
            return False
    return False

def run_migration():
    """Führt die Migration durch"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=" * 60)
    print("HolzbauERP - Datenbank Migration")
    print("=" * 60)
    
    try:
        # =====================================================
        # TENANTS TABELLE
        # =====================================================
        print("\n[1/8] Aktualisiere TENANTS Tabelle...")
        
        tenant_columns = [
            ('legal_form', 'VARCHAR(50)'),
            ('founding_date', 'TIMESTAMP'),
            ('tax_number', 'VARCHAR(50)'),
            ('trade_register_court', 'VARCHAR(100)'),
            ('chamber_of_crafts', 'VARCHAR(100)'),
            ('chamber_membership_number', 'VARCHAR(50)'),
            ('ceo_name', 'VARCHAR(100)'),
            ('authorized_signatories', 'TEXT'),
            ('phone_secondary', 'VARCHAR(30)'),
            ('fax', 'VARCHAR(30)'),
            ('mobile', 'VARCHAR(30)'),
            ('linkedin_url', 'VARCHAR(255)'),
            ('facebook_url', 'VARCHAR(255)'),
            ('instagram_url', 'VARCHAR(255)'),
            ('xing_url', 'VARCHAR(255)'),
            ('address_addition', 'VARCHAR(100)'),
            ('district', 'VARCHAR(100)'),
            ('state', 'VARCHAR(100)'),
            ('country_code', 'VARCHAR(3)'),
            ('latitude', 'VARCHAR(20)'),
            ('longitude', 'VARCHAR(20)'),
            ('altitude', 'VARCHAR(20)'),
            ('bank_name', 'VARCHAR(100)'),
            ('bank_account_holder', 'VARCHAR(100)'),
            ('secondary_bank_name', 'VARCHAR(100)'),
            ('secondary_iban', 'VARCHAR(34)'),
            ('secondary_bic', 'VARCHAR(11)'),
            ('paypal_email', 'VARCHAR(255)'),
            ('stripe_account_id', 'VARCHAR(100)'),
            ('certifications', 'TEXT'),
            ('quality_management', 'VARCHAR(100)'),
            ('environmental_certification', 'VARCHAR(100)'),
            ('safety_certification', 'VARCHAR(100)'),
            ('master_craftsman_certificate', 'VARCHAR(100)'),
            ('master_craftsman_name', 'VARCHAR(100)'),
            ('guild_membership', 'VARCHAR(100)'),
            ('trade_association', 'VARCHAR(100)'),
            ('liability_insurance', 'VARCHAR(100)'),
            ('liability_coverage', 'VARCHAR(50)'),
            ('building_insurance', 'VARCHAR(100)'),
            ('professional_indemnity', 'VARCHAR(100)'),
            ('insurance_policy_number', 'VARCHAR(50)'),
            ('insurance_valid_until', 'TIMESTAMP'),
            ('employee_count', 'VARCHAR(10)'),
            ('apprentice_count', 'VARCHAR(10)'),
            ('annual_revenue', 'VARCHAR(50)'),
            ('production_facility_address', 'TEXT'),
            ('storage_facility_address', 'TEXT'),
            ('wood_types_offered', 'TEXT'),
            ('specializations', 'TEXT'),
            ('service_radius_km', 'VARCHAR(10)'),
            ('invoice_prefix', 'VARCHAR(20)'),
            ('invoice_number_format', 'VARCHAR(50)'),
            ('next_invoice_number', 'VARCHAR(10)'),
            ('offer_prefix', 'VARCHAR(20)'),
            ('offer_validity_days', 'VARCHAR(10)'),
            ('default_payment_terms', 'VARCHAR(10)'),
            ('default_vat_rate', 'VARCHAR(10)'),
            ('default_currency', 'VARCHAR(3)'),
            ('invoice_footer_text', 'TEXT'),
            ('email_signature', 'TEXT'),
            ('smtp_host', 'VARCHAR(255)'),
            ('smtp_port', 'VARCHAR(10)'),
            ('smtp_user', 'VARCHAR(255)'),
            ('smtp_password', 'VARCHAR(255)'),
            ('smtp_use_tls', 'BOOLEAN'),
            ('working_hours_start', 'VARCHAR(10)'),
            ('working_hours_end', 'VARCHAR(10)'),
            ('working_days', 'VARCHAR(20)'),
            ('fiscal_year_start_month', 'VARCHAR(10)'),
            ('data_retention_years', 'VARCHAR(10)'),
            ('gdpr_contact_email', 'VARCHAR(255)'),
            ('custom_fields', 'TEXT'),
            ('extra_data', 'TEXT'),
        ]
        
        if table_exists(cursor, 'tenants'):
            for col_name, col_type in tenant_columns:
                add_column_if_not_exists(cursor, 'tenants', col_name, col_type)
        
        # =====================================================
        # CUSTOMERS TABELLE
        # =====================================================
        print("\n[2/8] Aktualisiere CUSTOMERS Tabelle...")
        
        customer_columns = [
            ('company_name_addition', 'VARCHAR(255)'),
            ('legal_form', 'VARCHAR(50)'),
            ('tax_number', 'VARCHAR(50)'),
            ('trade_register_court', 'VARCHAR(100)'),
            ('industry', 'VARCHAR(100)'),
            ('company_size', 'VARCHAR(50)'),
            ('founding_year', 'VARCHAR(4)'),
            ('title', 'VARCHAR(50)'),
            ('date_of_birth', 'DATE'),
            ('nationality', 'VARCHAR(100)'),
            ('language', 'VARCHAR(10)'),
            ('email_secondary', 'VARCHAR(255)'),
            ('email_invoice', 'VARCHAR(255)'),
            ('phone_direct', 'VARCHAR(50)'),
            ('phone_secondary', 'VARCHAR(50)'),
            ('linkedin_url', 'VARCHAR(255)'),
            ('xing_url', 'VARCHAR(255)'),
            ('preferred_contact_method', 'VARCHAR(50)'),
            ('preferred_contact_time', 'VARCHAR(100)'),
            ('newsletter_subscribed', 'BOOLEAN'),
            ('marketing_consent', 'BOOLEAN'),
            ('marketing_consent_date', 'TIMESTAMP'),
            ('address_addition', 'VARCHAR(100)'),
            ('district', 'VARCHAR(100)'),
            ('country_code', 'VARCHAR(3)'),
            ('latitude', 'VARCHAR(20)'),
            ('longitude', 'VARCHAR(20)'),
            ('payment_method', 'VARCHAR(50)'),
            ('early_payment_discount', 'VARCHAR(10)'),
            ('early_payment_days', 'VARCHAR(10)'),
            ('account_holder', 'VARCHAR(255)'),
            ('sepa_mandate', 'VARCHAR(100)'),
            ('sepa_mandate_date', 'DATE'),
            ('debitor_number', 'VARCHAR(50)'),
            ('cost_center', 'VARCHAR(50)'),
            ('revenue_account', 'VARCHAR(50)'),
            ('subcategory', 'VARCHAR(100)'),
            ('customer_group', 'VARCHAR(100)'),
            ('customer_class', 'VARCHAR(10)'),
            ('price_group', 'VARCHAR(50)'),
            ('rating', 'INTEGER'),
            ('credit_rating', 'VARCHAR(50)'),
            ('credit_rating_date', 'DATE'),
            ('source_detail', 'VARCHAR(255)'),
            ('referral_customer_id', 'UUID'),
            ('first_contact_date', 'DATE'),
            ('acquisition_date', 'DATE'),
            ('sales_person_id', 'UUID'),
            ('account_manager_id', 'UUID'),
            ('total_revenue', 'VARCHAR(20)'),
            ('total_projects', 'INTEGER'),
            ('last_project_date', 'DATE'),
            ('last_contact_date', 'DATE'),
            ('last_invoice_date', 'DATE'),
            ('open_invoices_amount', 'VARCHAR(20)'),
            ('payment_notes', 'TEXT'),
            ('tags', 'TEXT[]'),
            ('is_active', 'BOOLEAN'),
            ('is_blocked', 'BOOLEAN'),
            ('blocked_reason', 'TEXT'),
            ('blocked_date', 'TIMESTAMP'),
            ('data_processing_consent', 'BOOLEAN'),
            ('data_processing_consent_date', 'TIMESTAMP'),
        ]
        
        if table_exists(cursor, 'customers'):
            for col_name, col_type in customer_columns:
                add_column_if_not_exists(cursor, 'customers', col_name, col_type)
        
        # =====================================================
        # MATERIALS TABELLE
        # =====================================================
        print("\n[3/8] Aktualisiere MATERIALS Tabelle...")
        
        material_columns = [
            ('gtin', 'VARCHAR(20)'),
            ('manufacturer_number', 'VARCHAR(100)'),
            ('name_short', 'VARCHAR(100)'),
            ('description_long', 'TEXT'),
            ('subcategory', 'VARCHAR(100)'),
            ('product_group', 'VARCHAR(100)'),
            ('product_line', 'VARCHAR(100)'),
            ('brand', 'VARCHAR(100)'),
            ('manufacturer_url', 'VARCHAR(500)'),
            ('length_tolerance_mm', 'VARCHAR(20)'),
            ('width_tolerance_mm', 'VARCHAR(20)'),
            ('height_tolerance_mm', 'VARCHAR(20)'),
            ('diameter_mm', 'INTEGER'),
            ('thread_size', 'VARCHAR(20)'),
            ('weight_per_meter', 'VARCHAR(20)'),
            ('weight_per_sqm', 'VARCHAR(20)'),
            ('volume_m3', 'VARCHAR(20)'),
            ('base_unit', 'VARCHAR(20)'),
            ('sales_unit', 'VARCHAR(20)'),
            ('purchase_unit', 'VARCHAR(20)'),
            ('unit_conversion', 'JSONB'),
            ('packaging_unit', 'VARCHAR(50)'),
            ('pieces_per_package', 'INTEGER'),
            ('packages_per_pallet', 'INTEGER'),
            ('pallet_quantity', 'INTEGER'),
            ('wood_type_latin', 'VARCHAR(100)'),
            ('wood_origin', 'VARCHAR(100)'),
            ('strength_class', 'VARCHAR(20)'),
            ('appearance_class', 'VARCHAR(20)'),
            ('moisture_content_min', 'VARCHAR(10)'),
            ('moisture_content_max', 'VARCHAR(10)'),
            ('surface_treatment', 'VARCHAR(100)'),
            ('impregnation', 'VARCHAR(100)'),
            ('fire_protection_class', 'VARCHAR(20)'),
            ('certification_number', 'VARCHAR(100)'),
            ('declaration_of_performance', 'VARCHAR(100)'),
            ('density_kg_m3', 'VARCHAR(20)'),
            ('bending_strength_mpa', 'VARCHAR(20)'),
            ('tensile_strength_mpa', 'VARCHAR(20)'),
            ('compression_strength_mpa', 'VARCHAR(20)'),
            ('shear_strength_mpa', 'VARCHAR(20)'),
            ('e_modulus_mpa', 'VARCHAR(20)'),
            ('thermal_conductivity', 'VARCHAR(20)'),
            ('vapor_diffusion_resistance', 'VARCHAR(20)'),
            ('fire_reaction_class', 'VARCHAR(20)'),
            ('sound_insulation_rw', 'VARCHAR(20)'),
            ('head_type', 'VARCHAR(50)'),
            ('drive_type', 'VARCHAR(50)'),
            ('tip_type', 'VARCHAR(50)'),
            ('thread_type', 'VARCHAR(50)'),
            ('material_type', 'VARCHAR(100)'),
            ('coating', 'VARCHAR(100)'),
            ('corrosion_class', 'VARCHAR(20)'),
            ('eta_number', 'VARCHAR(100)'),
            ('approval_document', 'VARCHAR(255)'),
            ('characteristic_load_capacity', 'VARCHAR(100)'),
            ('purchase_price_date', 'DATE'),
            ('list_price', 'VARCHAR(20)'),
            ('minimum_price', 'VARCHAR(20)'),
            ('margin_percent', 'VARCHAR(10)'),
            ('markup_percent', 'VARCHAR(10)'),
            ('tax_rate', 'VARCHAR(10)'),
            ('price_scales', 'JSONB'),
            ('max_stock', 'VARCHAR(20)'),
            ('safety_stock', 'VARCHAR(20)'),
            ('reorder_point', 'VARCHAR(20)'),
            ('reorder_quantity', 'VARCHAR(20)'),
            ('lot_size', 'VARCHAR(20)'),
            ('reserved_stock', 'VARCHAR(20)'),
            ('available_stock', 'VARCHAR(20)'),
            ('ordered_stock', 'VARCHAR(20)'),
            ('average_consumption', 'VARCHAR(20)'),
            ('last_purchase_date', 'DATE'),
            ('last_sale_date', 'DATE'),
            ('turnover_rate', 'VARCHAR(10)'),
            ('supplier_article_number', 'VARCHAR(100)'),
            ('lead_time_days', 'INTEGER'),
            ('minimum_order_quantity', 'VARCHAR(20)'),
            ('storage_conditions', 'TEXT'),
            ('shelf_life_days', 'INTEGER'),
            ('is_producible', 'BOOLEAN'),
            ('is_purchasable', 'BOOLEAN'),
            ('is_sellable', 'BOOLEAN'),
            ('is_stockable', 'BOOLEAN'),
            ('is_serial_tracked', 'BOOLEAN'),
            ('is_batch_tracked', 'BOOLEAN'),
            ('is_hazardous', 'BOOLEAN'),
            ('status', 'VARCHAR(50)'),
            ('discontinued_date', 'DATE'),
            ('replacement_article_id', 'UUID'),
            ('image_urls', 'JSONB'),
            ('datasheet_url', 'VARCHAR(500)'),
            ('safety_datasheet_url', 'VARCHAR(500)'),
            ('installation_guide_url', 'VARCHAR(500)'),
            ('video_url', 'VARCHAR(500)'),
            ('purchase_notes', 'TEXT'),
            ('production_notes', 'TEXT'),
            ('tags', 'TEXT[]'),
            ('technical_data', 'JSONB'),
        ]
        
        if table_exists(cursor, 'materials'):
            for col_name, col_type in material_columns:
                add_column_if_not_exists(cursor, 'materials', col_name, col_type)
        
        # =====================================================
        # PROJECTS TABELLE
        # =====================================================
        print("\n[4/8] Aktualisiere PROJECTS Tabelle...")
        
        project_columns = [
            ('short_description', 'VARCHAR(500)'),
            ('sub_status', 'VARCHAR(100)'),
            ('site_manager_id', 'UUID'),
            ('sales_person_id', 'UUID'),
            ('architect_company', 'VARCHAR(255)'),
            ('architect_email', 'VARCHAR(255)'),
            ('architect_phone', 'VARCHAR(50)'),
            ('structural_engineer_name', 'VARCHAR(255)'),
            ('structural_engineer_company', 'VARCHAR(255)'),
            ('structural_engineer_email', 'VARCHAR(255)'),
            ('structural_engineer_phone', 'VARCHAR(50)'),
            ('energy_consultant_name', 'VARCHAR(255)'),
            ('energy_consultant_company', 'VARCHAR(255)'),
            ('general_contractor_name', 'VARCHAR(255)'),
            ('general_contractor_company', 'VARCHAR(255)'),
            ('inquiry_date', 'DATE'),
            ('quote_date', 'DATE'),
            ('quote_deadline', 'DATE'),
            ('decision_date', 'DATE'),
            ('order_date', 'DATE'),
            ('contract_signing_date', 'DATE'),
            ('planning_start', 'DATE'),
            ('planning_end', 'DATE'),
            ('production_start', 'DATE'),
            ('production_end', 'DATE'),
            ('delivery_date', 'DATE'),
            ('acceptance_date', 'DATE'),
            ('warranty_end_date', 'DATE'),
            ('site_name', 'VARCHAR(255)'),
            ('site_address_addition', 'VARCHAR(100)'),
            ('site_district', 'VARCHAR(100)'),
            ('site_state', 'VARCHAR(100)'),
            ('site_altitude', 'VARCHAR(20)'),
            ('site_geohash', 'VARCHAR(20)'),
            ('site_parcel_number', 'VARCHAR(50)'),
            ('site_cadastral_district', 'VARCHAR(100)'),
            ('site_land_register', 'VARCHAR(100)'),
            ('site_what3words', 'VARCHAR(100)'),
            ('site_access_description', 'TEXT'),
            ('site_access_restrictions', 'TEXT'),
            ('site_access_width_m', 'VARCHAR(10)'),
            ('site_access_height_m', 'VARCHAR(10)'),
            ('site_access_weight_limit', 'VARCHAR(10)'),
            ('site_crane_setup_possible', 'BOOLEAN'),
            ('site_crane_setup_location', 'TEXT'),
            ('site_storage_area_available', 'BOOLEAN'),
            ('site_storage_area_sqm', 'VARCHAR(20)'),
            ('site_electricity_available', 'BOOLEAN'),
            ('site_water_available', 'BOOLEAN'),
            ('site_toilet_available', 'BOOLEAN'),
            ('site_parking_description', 'TEXT'),
            ('site_special_conditions', 'TEXT'),
            ('building_class', 'VARCHAR(50)'),
            ('building_use', 'VARCHAR(100)'),
            ('gross_floor_area', 'VARCHAR(20)'),
            ('net_floor_area', 'VARCHAR(20)'),
            ('living_space', 'VARCHAR(20)'),
            ('usable_area', 'VARCHAR(20)'),
            ('basement_area', 'VARCHAR(20)'),
            ('roof_area', 'VARCHAR(20)'),
            ('facade_area', 'VARCHAR(20)'),
            ('floors_above_ground', 'INTEGER'),
            ('floors_below_ground', 'INTEGER'),
            ('attic_type', 'VARCHAR(50)'),
            ('building_length_m', 'VARCHAR(20)'),
            ('building_width_m', 'VARCHAR(20)'),
            ('building_height_m', 'VARCHAR(20)'),
            ('ridge_height_m', 'VARCHAR(20)'),
            ('eaves_height_m', 'VARCHAR(20)'),
            ('roof_type', 'VARCHAR(50)'),
            ('roof_pitch', 'VARCHAR(20)'),
            ('roof_pitch_secondary', 'VARCHAR(20)'),
            ('roof_overhang_eaves', 'VARCHAR(20)'),
            ('roof_overhang_gable', 'VARCHAR(20)'),
            ('roof_covering', 'VARCHAR(100)'),
            ('wood_volume_m3', 'VARCHAR(20)'),
            ('wood_type_primary', 'VARCHAR(100)'),
            ('wood_type_secondary', 'VARCHAR(100)'),
            ('wood_quality', 'VARCHAR(50)'),
            ('wood_moisture', 'VARCHAR(20)'),
            ('wood_certification', 'VARCHAR(50)'),
            ('wall_construction', 'VARCHAR(100)'),
            ('wall_thickness_cm', 'VARCHAR(20)'),
            ('ceiling_construction', 'VARCHAR(100)'),
            ('roof_construction', 'VARCHAR(100)'),
            ('prefabrication_degree', 'VARCHAR(50)'),
            ('module_count', 'INTEGER'),
            ('insulation_standard', 'VARCHAR(50)'),
            ('energy_efficiency_class', 'VARCHAR(10)'),
            ('primary_energy_demand', 'VARCHAR(20)'),
            ('heating_demand', 'VARCHAR(20)'),
            ('u_value_wall', 'VARCHAR(20)'),
            ('u_value_roof', 'VARCHAR(20)'),
            ('u_value_floor', 'VARCHAR(20)'),
            ('blower_door_value', 'VARCHAR(20)'),
            ('heating_system', 'VARCHAR(100)'),
            ('ventilation_system', 'VARCHAR(100)'),
            ('solar_system', 'VARCHAR(100)'),
            ('building_permit_required', 'BOOLEAN'),
            ('building_permit_number', 'VARCHAR(100)'),
            ('building_permit_date', 'DATE'),
            ('building_permit_authority', 'VARCHAR(255)'),
            ('building_permit_status', 'VARCHAR(50)'),
            ('structural_approval', 'VARCHAR(100)'),
            ('structural_approval_date', 'DATE'),
            ('fire_safety_concept', 'BOOLEAN'),
            ('fire_resistance_class', 'VARCHAR(20)'),
            ('noise_protection_class', 'VARCHAR(20)'),
            ('earthquake_zone', 'VARCHAR(20)'),
            ('snow_load_zone', 'VARCHAR(20)'),
            ('wind_load_zone', 'VARCHAR(20)'),
            ('budget_materials', 'VARCHAR(20)'),
            ('budget_labor', 'VARCHAR(20)'),
            ('budget_external', 'VARCHAR(20)'),
            ('budget_other', 'VARCHAR(20)'),
            ('actual_cost_materials', 'VARCHAR(20)'),
            ('actual_cost_labor', 'VARCHAR(20)'),
            ('actual_cost_external', 'VARCHAR(20)'),
            ('margin_percent', 'VARCHAR(10)'),
            ('margin_amount', 'VARCHAR(20)'),
            ('subsidy_program', 'VARCHAR(255)'),
            ('subsidy_amount', 'VARCHAR(20)'),
            ('subsidy_status', 'VARCHAR(50)'),
            ('planned_hours_total', 'VARCHAR(20)'),
            ('planned_hours_planning', 'VARCHAR(20)'),
            ('planned_hours_production', 'VARCHAR(20)'),
            ('planned_hours_assembly', 'VARCHAR(20)'),
            ('actual_hours_total', 'VARCHAR(20)'),
            ('actual_hours_planning', 'VARCHAR(20)'),
            ('actual_hours_production', 'VARCHAR(20)'),
            ('actual_hours_assembly', 'VARCHAR(20)'),
            ('progress_overall', 'INTEGER'),
            ('progress_planning', 'INTEGER'),
            ('progress_production', 'INTEGER'),
            ('progress_assembly', 'INTEGER'),
            ('complexity', 'VARCHAR(20)'),
            ('risk_level', 'VARCHAR(20)'),
            ('strategic_importance', 'VARCHAR(20)'),
            ('contract_type', 'VARCHAR(100)'),
            ('warranty_months', 'INTEGER'),
            ('retention_percent', 'VARCHAR(10)'),
            ('retention_amount', 'VARCHAR(20)'),
            ('performance_bond', 'BOOLEAN'),
            ('quality_requirements', 'TEXT'),
            ('inspection_plan_required', 'BOOLEAN'),
            ('acceptance_criteria', 'TEXT'),
            ('communication_channel', 'VARCHAR(50)'),
            ('report_frequency', 'VARCHAR(50)'),
            ('next_meeting_date', 'TIMESTAMP'),
            ('is_reference_project', 'BOOLEAN'),
            ('reference_approved', 'BOOLEAN'),
            ('photo_permission', 'BOOLEAN'),
            ('publication_allowed', 'BOOLEAN'),
            ('risk_notes', 'TEXT'),
            ('tags', 'TEXT[]'),
            ('extra_metadata', 'JSONB'),
        ]
        
        if table_exists(cursor, 'projects'):
            for col_name, col_type in project_columns:
                add_column_if_not_exists(cursor, 'projects', col_name, col_type)
        
        # =====================================================
        # CONSTRUCTION_DIARIES TABELLE ERSTELLEN
        # =====================================================
        print("\n[5/8] Erstelle CONSTRUCTION_DIARIES Tabelle...")
        
        if not table_exists(cursor, 'construction_diaries'):
            cursor.execute("""
                CREATE TABLE construction_diaries (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    diary_number VARCHAR(50) NOT NULL,
                    project_id UUID REFERENCES projects(id),
                    diary_date DATE NOT NULL,
                    calendar_week INTEGER,
                    work_start_time TIME,
                    work_end_time TIME,
                    break_duration_minutes INTEGER DEFAULT 0,
                    effective_work_hours VARCHAR(10),
                    weather_morning VARCHAR(50),
                    weather_afternoon VARCHAR(50),
                    weather_evening VARCHAR(50),
                    temperature_morning VARCHAR(10),
                    temperature_afternoon VARCHAR(10),
                    temperature_min VARCHAR(10),
                    temperature_max VARCHAR(10),
                    humidity_percent VARCHAR(10),
                    wind_speed_kmh VARCHAR(10),
                    wind_direction VARCHAR(20),
                    precipitation_mm VARCHAR(10),
                    weather_notes TEXT,
                    work_possible BOOLEAN DEFAULT TRUE,
                    weather_delay_hours VARCHAR(10),
                    own_workers_count INTEGER DEFAULT 0,
                    subcontractor_workers_count INTEGER DEFAULT 0,
                    total_workers INTEGER DEFAULT 0,
                    personnel_details JSONB DEFAULT '[]',
                    subcontractors_present JSONB DEFAULT '[]',
                    equipment_used JSONB DEFAULT '[]',
                    crane_hours VARCHAR(10),
                    equipment_notes TEXT,
                    work_performed TEXT,
                    work_location VARCHAR(255),
                    trades_active TEXT[],
                    progress_description TEXT,
                    progress_percent INTEGER,
                    milestones_reached JSONB DEFAULT '[]',
                    deliveries JSONB DEFAULT '[]',
                    materials_used JSONB DEFAULT '[]',
                    visitors JSONB DEFAULT '[]',
                    meetings_held JSONB DEFAULT '[]',
                    incidents JSONB DEFAULT '[]',
                    delays JSONB DEFAULT '[]',
                    problems_encountered TEXT,
                    solutions_applied TEXT,
                    instructions_received JSONB DEFAULT '[]',
                    change_orders JSONB DEFAULT '[]',
                    quality_checks JSONB DEFAULT '[]',
                    inspections JSONB DEFAULT '[]',
                    safety_briefing_done BOOLEAN DEFAULT FALSE,
                    safety_issues TEXT,
                    safety_measures TEXT,
                    photos JSONB DEFAULT '[]',
                    photo_count INTEGER DEFAULT 0,
                    planned_work_tomorrow TEXT,
                    planned_personnel_tomorrow INTEGER,
                    required_materials_tomorrow TEXT,
                    required_equipment_tomorrow TEXT,
                    site_manager_signature VARCHAR(255),
                    site_manager_signed_at TIMESTAMP,
                    client_signature VARCHAR(255),
                    client_signed_at TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'draft',
                    submitted_at TIMESTAMP,
                    approved_by UUID,
                    approved_at TIMESTAMP,
                    notes TEXT,
                    internal_notes TEXT,
                    custom_fields JSONB DEFAULT '{}',
                    tenant_id UUID REFERENCES tenants(id),
                    created_by UUID,
                    updated_by UUID,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    is_deleted BOOLEAN DEFAULT FALSE,
                    deleted_at TIMESTAMP
                )
            """)
            print("  ✓ Tabelle construction_diaries erstellt")
            
            cursor.execute("CREATE INDEX idx_construction_diaries_project ON construction_diaries(project_id)")
            cursor.execute("CREATE INDEX idx_construction_diaries_date ON construction_diaries(diary_date)")
            cursor.execute("CREATE INDEX idx_construction_diaries_tenant ON construction_diaries(tenant_id)")
        
        # =====================================================
        # SUPPLIERS TABELLE
        # =====================================================
        print("\n[6/8] Erstelle SUPPLIERS Tabelle...")
        
        if not table_exists(cursor, 'suppliers'):
            cursor.execute("""
                CREATE TABLE suppliers (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    supplier_number VARCHAR(50) NOT NULL,
                    company_name VARCHAR(255) NOT NULL,
                    tax_id VARCHAR(50),
                    contact_person VARCHAR(200),
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    fax VARCHAR(50),
                    website VARCHAR(255),
                    street VARCHAR(255),
                    street_number VARCHAR(20),
                    postal_code VARCHAR(20),
                    city VARCHAR(100),
                    country VARCHAR(100) DEFAULT 'Deutschland',
                    payment_terms VARCHAR(10) DEFAULT '30',
                    iban VARCHAR(50),
                    bic VARCHAR(20),
                    rating INTEGER,
                    notes TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    tenant_id UUID REFERENCES tenants(id),
                    created_by UUID,
                    updated_by UUID,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    is_deleted BOOLEAN DEFAULT FALSE,
                    deleted_at TIMESTAMP
                )
            """)
            print("  ✓ Tabelle suppliers erstellt")
            
            cursor.execute("CREATE INDEX idx_suppliers_number ON suppliers(supplier_number)")
            cursor.execute("CREATE INDEX idx_suppliers_tenant ON suppliers(tenant_id)")
        
        # =====================================================
        # WAREHOUSES TABELLE
        # =====================================================
        print("\n[7/8] Erstelle WAREHOUSES Tabelle...")
        
        if not table_exists(cursor, 'warehouses'):
            cursor.execute("""
                CREATE TABLE warehouses (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    code VARCHAR(20) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    street VARCHAR(255),
                    street_number VARCHAR(20),
                    postal_code VARCHAR(20),
                    city VARCHAR(100),
                    is_default BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    tenant_id UUID REFERENCES tenants(id),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    is_deleted BOOLEAN DEFAULT FALSE,
                    deleted_at TIMESTAMP
                )
            """)
            print("  ✓ Tabelle warehouses erstellt")
        
        if not table_exists(cursor, 'warehouse_locations'):
            cursor.execute("""
                CREATE TABLE warehouse_locations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    warehouse_id UUID REFERENCES warehouses(id),
                    code VARCHAR(50) NOT NULL,
                    name VARCHAR(255),
                    description TEXT,
                    max_weight_kg INTEGER,
                    length_mm INTEGER,
                    width_mm INTEGER,
                    height_mm INTEGER,
                    location_type VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            print("  ✓ Tabelle warehouse_locations erstellt")
        
        # =====================================================
        # Fehlende Foreign Key Spalten in materials
        # =====================================================
        print("\n[8/8] Füge Foreign Keys hinzu...")
        
        if table_exists(cursor, 'materials'):
            add_column_if_not_exists(cursor, 'materials', 'primary_supplier_id', 'UUID')
            add_column_if_not_exists(cursor, 'materials', 'default_location_id', 'UUID')
        
        # Commit
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✓ Migration erfolgreich abgeschlossen!")
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Fehler bei der Migration: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migration()
