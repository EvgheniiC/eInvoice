/**
 * Generated from FastAPI OpenAPI by backend/scripts/export_openapi.py.
 * Do not edit by hand.
 */

export interface components {
  schemas: {
    AccountantPackageRequest: {
      invoice: components["schemas"]["InvoiceParseResponse-Input"];
      pdf_base64?: string | null;
      pdf_filename?: string | null;
      xml_base64?: string | null;
      xml_filename?: string | null;
    };
    Body_parse_invoice_api_invoices_parse_post: {
      file: string;
    };
    CapabilitiesResponse: {
      max_upload_size_mb: number;
      allowed_extensions: string[];
      max_files_per_request: number;
      rate_limit_per_minute: number;
      stores_invoice_files: boolean;
      requires_account: boolean;
      processing_model: string;
      standard_version: string;
      xrechnung_version: string;
      formats: components["schemas"]["SupportedFormat"][];
      profiles: string[];
      limitations: string[];
    };
    ExportFormat: "csv" | "excel" | "datev";
    ExportMappingDoc: {
      format: components["schemas"]["ExportFormat"];
      version: string;
      description: string;
      columns: string[];
      encoding: string;
      delimiter: string;
      decimal_separator: string;
      date_format: string;
      notes: string | null;
      limitations: string | null;
    };
    ExportRequest: {
      format?: components["schemas"]["ExportFormat"];
      invoice: components["schemas"]["InvoiceParseResponse-Input"];
    };
    FeedbackRequest: {
      message: string;
      contact_email?: string | null;
    };
    FeedbackResponse: {
      accepted: boolean;
      message: string;
    };
    FunnelEventRequest: {
      step: "landing" | "upload";
    };
    FunnelEventResponse: {
      accepted: boolean;
    };
    HTTPValidationError: {
      detail?: components["schemas"]["ValidationError"][];
    };
    HealthCheck: {
      name: string;
      status: string;
      detail: string | null;
    };
    HealthResponse: {
      status: string;
      ready: boolean;
      app_name: string;
      version: string;
      environment: string;
      kosit_required: boolean;
      kosit_ready: boolean;
      checks: components["schemas"]["HealthCheck"][];
    };
    "InvoiceParseResponse-Input": {
      status: components["schemas"]["ParseStatus"];
      message: string;
      filename: string;
      file_type?: string | null;
      document_type?: "invoice" | "credit_note" | null;
      invoice_number?: string | null;
      issue_date?: string | null;
      due_date?: string | null;
      seller?: components["schemas"]["PartyInfo-Input"] | null;
      buyer?: components["schemas"]["PartyInfo-Input"] | null;
      totals?: components["schemas"]["InvoiceTotals-Input"] | null;
      line_items?: components["schemas"]["LineItem-Input"][];
      payment_reference?: string | null;
      validation_status?: components["schemas"]["ValidationStatus"];
      validation_meta?: components["schemas"]["ValidationMeta-Input"];
      validation_issues?: components["schemas"]["ValidationIssue-Input"][];
      mismatch_warnings?: string[];
      mismatch_fields?: components["schemas"]["MismatchField-Input"][];
      next_steps?: string[];
    };
    "InvoiceParseResponse-Output": {
      status: components["schemas"]["ParseStatus"];
      message: string;
      filename: string;
      file_type: string | null;
      document_type: "invoice" | "credit_note" | null;
      invoice_number: string | null;
      issue_date: string | null;
      due_date: string | null;
      seller: components["schemas"]["PartyInfo-Output"] | null;
      buyer: components["schemas"]["PartyInfo-Output"] | null;
      totals: components["schemas"]["InvoiceTotals-Output"] | null;
      line_items: components["schemas"]["LineItem-Output"][];
      payment_reference: string | null;
      validation_status: components["schemas"]["ValidationStatus"];
      validation_meta: components["schemas"]["ValidationMeta-Output"];
      validation_issues: components["schemas"]["ValidationIssue-Output"][];
      mismatch_warnings: string[];
      mismatch_fields: components["schemas"]["MismatchField-Output"][];
      next_steps: string[];
    };
    "InvoiceTotals-Input": {
      net?: number | string | null;
      tax?: number | string | null;
      gross?: number | string | null;
      currency?: string | null;
      allowance?: number | string | null;
      charge?: number | string | null;
      tax_breakdown?: components["schemas"]["TaxBreakdown-Input"][];
    };
    "InvoiceTotals-Output": {
      net: string | null;
      tax: string | null;
      gross: string | null;
      currency: string | null;
      allowance: string | null;
      charge: string | null;
      tax_breakdown: components["schemas"]["TaxBreakdown-Output"][];
    };
    "LineItem-Input": {
      position?: number | null;
      description?: string | null;
      quantity?: number | string | null;
      unit?: string | null;
      unit_price?: number | string | null;
      tax_rate?: number | string | null;
      net_amount?: number | string | null;
      gross_amount?: number | string | null;
    };
    "LineItem-Output": {
      position: number | null;
      description: string | null;
      quantity: string | null;
      unit: string | null;
      unit_price: string | null;
      tax_rate: string | null;
      net_amount: string | null;
      gross_amount: string | null;
    };
    LivenessResponse: {
      status: string;
    };
    "MismatchField-Input": {
      field: string;
      label: string;
      xml_value?: string | null;
      pdf_value?: string | null;
      matched: boolean;
    };
    "MismatchField-Output": {
      field: string;
      label: string;
      xml_value: string | null;
      pdf_value: string | null;
      matched: boolean;
    };
    ParseStatus: "success" | "partial" | "error" | "not_implemented";
    "PartyInfo-Input": {
      name?: string | null;
      address?: string | null;
      vat_id?: string | null;
      iban?: string | null;
    };
    "PartyInfo-Output": {
      name: string | null;
      address: string | null;
      vat_id: string | null;
      iban: string | null;
    };
    ReadinessResponse: {
      status: string;
      ready: boolean;
      checks: components["schemas"]["HealthCheck"][];
    };
    SupportedFormat: {
      id: string;
      label: string;
      extensions: string[];
      notes: string;
    };
    "TaxBreakdown-Input": {
      rate: number | string;
      amount?: number | string | null;
    };
    "TaxBreakdown-Output": {
      rate: string;
      amount: string | null;
    };
    ValidationError: {
      loc: (string | number)[];
      msg: string;
      type: string;
      input?: unknown;
      ctx?: Record<string, unknown>;
    };
    "ValidationIssue-Input": {
      level: string;
      category?: string;
      code?: string | null;
      message: string;
      explanation?: string | null;
      bt_code?: string | null;
      field?: string | null;
    };
    "ValidationIssue-Output": {
      level: string;
      category: string;
      code: string | null;
      message: string;
      explanation: string | null;
      bt_code: string | null;
      field: string | null;
    };
    "ValidationMeta-Input": {
      standard_version?: string | null;
      profile?: string | null;
      profile_id?: string | null;
      engine?: string;
      engine_version?: string | null;
      scenarios_version?: string | null;
      full_check_completed?: boolean;
    };
    "ValidationMeta-Output": {
      standard_version: string | null;
      profile: string | null;
      profile_id: string | null;
      engine: string;
      engine_version: string | null;
      scenarios_version: string | null;
      full_check_completed: boolean;
    };
    ValidationReportRequest: {
      invoice: components["schemas"]["InvoiceParseResponse-Input"];
    };
    ValidationStatus: "valid" | "invalid" | "warning" | "not_checked";
  };
}
