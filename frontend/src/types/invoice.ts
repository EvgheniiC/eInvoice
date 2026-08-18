/**
 * Frontend DTO aliases for FastAPI OpenAPI schemas.
 *
 * Source of truth: backend Pydantic models.
 * Regenerate with: python backend/scripts/export_openapi.py
 */
import type { components } from './openapi'

type Schemas = components['schemas']

export type ParseStatus = Schemas['ParseStatus']
export type ValidationStatus = Schemas['ValidationStatus']
export type ExportFormat = Schemas['ExportFormat']
export type PartyInfo = Schemas['PartyInfo-Output']
export type LineItem = Schemas['LineItem-Output']
export type TaxBreakdown = Schemas['TaxBreakdown-Output']
export type InvoiceTotals = Schemas['InvoiceTotals-Output']
export type ValidationIssue = Schemas['ValidationIssue-Output']
export type ValidationMeta = Schemas['ValidationMeta-Output']
export type MismatchField = Schemas['MismatchField-Output']
export type InvoiceParseResponse = Schemas['InvoiceParseResponse-Output']
export type HealthResponse = Schemas['HealthResponse']
export type HealthCheck = Schemas['HealthCheck']
export type LivenessResponse = Schemas['LivenessResponse']
export type ReadinessResponse = Schemas['ReadinessResponse']
export type ExportRequest = Schemas['ExportRequest']
export type ValidationReportRequest = Schemas['ValidationReportRequest']
export type AccountantPackageRequest = Schemas['AccountantPackageRequest']
export type CapabilitiesResponse = Schemas['CapabilitiesResponse']
export type SupportedFormat = Schemas['SupportedFormat']
export type FeedbackRequest = Schemas['FeedbackRequest']
export type FeedbackResponse = Schemas['FeedbackResponse']
export type FunnelEventRequest = Schemas['FunnelEventRequest']
export type FunnelEventResponse = Schemas['FunnelEventResponse']

/** UI helper: FastAPI serializes decimals as strings; Number() also accepts number. */
export type DecimalValue = string | number
