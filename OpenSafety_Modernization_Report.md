# OpenSafety: .NET Framework to .NET 8 Modernization Report

> **Status:** Assessment complete — pending go/no-go decision  
> **Date:** April 2026  
> **Basis:** Architecture and code-audit documentation. Findings marked *(inferred)* were derived from assessment documents rather than direct code validation.

---

## 1. Executive Summary

OpenSafety is a multi-tier .NET Framework application that has accumulated meaningful technical debt across its service, data, and presentation layers. The solution targets runtime versions that Microsoft no longer supports, carries security risks from hardcoded credentials, and relies on several frameworks — WCF, EF6, Unity DI, ASP.NET MVC 5, and `System.Web` — that have no direct equivalent in modern .NET.

This report recommends a **phased migration to .NET 8 LTS**, the current long-term support release supported until November 2026 for patch updates and beyond for security fixes. The migration is achievable in approximately **12–22 weeks** at a cost of **55–92 developer-days**, depending on team size and parallel workstream capacity. The modernized solution will be deployable to Azure App Service or Azure Container Apps, observable via Application Insights, and secured through Azure Key Vault — eliminating the current credential-in-source-control risk immediately.

---

## 2. Current State

The solution comprises approximately 18 projects in total. The table below summarises the composition as assessed from documentation.

| Category | Count | Target Framework | Notes |
|---|---|---|---|
| Active application projects | 10 | .NET Framework 4.7.1 | Core business logic, WCF, MVC 5, EF6 |
| Stub / scaffold projects | 4 | 4.7.1 / 4.5.2 | Candidates for removal or consolidation |
| Developer tooling projects | 2 | 4.7.1 / 4.5.2 | Build helpers; assess for retention |
| Existing modern utility | 1 | .NET Core 3.1 *(EOL)* | Upgrade-in-place to .NET 8 |

Key technology inventory:

- **Frontend:** ASP.NET MVC 5 backed by `System.Web` — incompatible with .NET 8 as-is.
- **Services:** WCF service host and generated client proxies — server-side WCF has no .NET 8 runtime.
- **Data access:** Entity Framework 6 — not portable to .NET 8 without migration to EF Core.
- **Dependency injection:** Unity IoC container — superseded by `Microsoft.Extensions.DependencyInjection`.
- **Background processing:** `ServiceBase` Windows Services — replaceable with `IHostedService`.
- **HTTP calls:** Synchronous `HttpClient` anti-patterns *(inferred)* — no `IHttpClientFactory`, no connection pooling.
- **Security:** Plaintext credentials in `Web.config` — confirmed risk from audit documentation.
- **Test coverage:** Minimal *(inferred)* — limited safety net for refactoring.

---

## 3. Why .NET 8

| Driver | Detail |
|---|---|
| **End of support** | .NET Framework 4.7.1 receives security patches only; no feature investment. .NET Core 3.1 (the existing utility) reached EOL in December 2022. |
| **Performance** | .NET 8 delivers measurably lower latency and higher throughput via Roslyn improvements, PGO, and a modernised runtime — directly relevant to service-layer endpoints. |
| **Security posture** | Modern authentication middleware, managed-identity support, and first-class Azure Key Vault integration replace the current plaintext-credential model. |
| **Cloud readiness** | .NET 8 applications deploy natively to Azure App Service, Container Apps, and AKS. `System.Web`-based applications require full IIS and cannot containerise cleanly. |
| **Ecosystem alignment** | Azure SDK, Application Insights SDK, and all current Microsoft NuGet packages target .NET 8 and `netstandard2.0`. Legacy packages will eventually lose support. |
| **LTS lifecycle** | .NET 8 is supported until November 2026, giving the team a stable, multi-year runway before the next required upgrade (to .NET 10 LTS). |

---

## 4. Migration Gaps and Blockers

The following represent the highest-effort and highest-risk items identified in the assessment.

**WCF (Critical).** .NET 8 does not host WCF services. All service contracts must be replaced with ASP.NET Core minimal APIs or gRPC. Existing client proxies must be rewritten using `HttpClient`/`Refit` or CoreWCF (community-supported client library) as a short-term bridge. A Strangler Fig pattern is recommended to migrate service by service within a running system.

**EF6 → EF Core (High).** EF6 is not portable to .NET 8 without code changes. Database-first scaffolding, LINQ query translation differences, and removed APIs (e.g., `ObjectContext`, lazy-loading defaults) require a migration pass. Schema compatibility can be preserved; only the C# data-access layer changes.

**Unity DI → Built-in DI (High).** Unity's registration API (`RegisterType`, `ResolveAll`) must be replaced with `IServiceCollection` equivalents. All composition roots need rewriting; however, the built-in container covers the majority of Unity scenarios and no additional package is required.

**System.Web / ASP.NET MVC 5 (High).** `HttpContext`, `HttpServerUtility`, `HttpPostedFile`, and all MVC 5 filter and routing infrastructure are unavailable in .NET 8. Controllers, filters, model binders, and routing must be rewritten as ASP.NET Core equivalents. View markup (Razor) is largely compatible.

**Windows Services (Medium).** `ServiceBase` is not available on .NET 8. Background services must be migrated to `IHostedService` / `BackgroundService` hosted by the Generic Host.

**Hardcoded credentials (Immediate).** `Web.config` connection strings and API keys must be externalised to Azure Key Vault or environment-variable configuration before any deployment pipeline is established.

**Synchronous I/O (Medium).** Widespread synchronous `HttpClient` usage and synchronous database calls *(inferred)* will limit scalability under load. Async/await conversion should accompany the framework migration.

---

## 5. Recommended Target Architecture

| Concern | Current | Target |
|---|---|---|
| Frontend | ASP.NET MVC 5 / `System.Web` | ASP.NET Core MVC / Razor Pages on .NET 8 |
| Services | WCF self-hosted | ASP.NET Core minimal APIs or gRPC |
| Data access | EF6 | EF Core 8 with Migrations |
| DI container | Unity | `Microsoft.Extensions.DependencyInjection` |
| Background work | Windows Service (`ServiceBase`) | `IHostedService` via Generic Host |
| HTTP clients | Direct `HttpClient` | `IHttpClientFactory` with named/typed clients |
| Configuration & secrets | `Web.config` / hardcoded | `appsettings.json` + Azure Key Vault |
| Hosting | IIS on-premises | Azure App Service or Azure Container Apps |
| Observability | None identified | Application Insights SDK + structured logging |
| Testing | Minimal | xUnit + Moq; test coverage targets per phase |

---

## 6. Phased Upgrade Plan

**Phase 1 — Foundation (Weeks 1–4)**  
Remove stub and scaffold projects. Centralise NuGet package versions. Migrate the existing `.NET Core 3.1` utility to .NET 8. Extract all credentials from `Web.config` to Azure Key Vault. Establish a CI/CD pipeline (GitHub Actions or Azure DevOps) gating on build and available tests. Create the `netstandard2.0` shared libraries as migration targets.

**Phase 2 — Data and DI (Weeks 4–9)**  
Migrate EF6 to EF Core 8. Replace Unity registrations with `IServiceCollection`. Introduce async data-access patterns. Validate via integration tests against a development database before decommissioning EF6.

**Phase 3 — Services (Weeks 7–14)**  
Apply Strangler Fig to WCF services: stand up ASP.NET Core minimal API endpoints alongside existing WCF endpoints, migrate consumers endpoint by endpoint, then decommission the WCF host once all consumers are on the new API surface.

**Phase 4 — Frontend and Background Services (Weeks 12–18)**  
Migrate ASP.NET MVC 5 controllers and views to ASP.NET Core. Replace `ServiceBase` Windows Services with `IHostedService`. Consolidate `IHttpClientFactory` usage. Connect Application Insights telemetry.

**Phase 5 — Validation and Hardening (Weeks 17–22)**  
Full regression and load testing. Security review (OWASP Top 10 pass). Performance baseline. Final decommission of all .NET Framework project targets. Production cut-over plan.

Phases 2–4 overlap intentionally to allow parallel workstreams once the Phase 1 shared foundation is stable.

---

## 7. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| WCF contract parity gaps discovered during migration | Medium | High | Prototype first service before committing full timeline; use CoreWCF as bridge |
| EF Core query incompatibilities break production queries | Medium | High | Run EF Core queries against production-representative data in staging before cut-over |
| Low test coverage allows regressions | High | High | Add targeted integration tests per module before migrating it |
| Team unfamiliarity with ASP.NET Core patterns | Medium | Medium | Allocate spike time in Phase 1; consider focused training |
| Credential leak during migration | Low | Critical | Immediate Key Vault integration in Phase 1; rotate secrets before first CI run |
| Timeline over-run due to hidden dependencies | Medium | Medium | Weekly progress reviews against phase gates; hold 20% schedule buffer |

---

## 8. Estimated Effort

Estimates are derived from the assessment documentation and should be validated against actual team velocity.

| Phase | Workstream | Developer-Days (Low) | Developer-Days (High) |
|---|---|---|---|
| 1 | Foundation, CI/CD, credential extraction | 8 | 12 |
| 2 | EF Core migration, DI replacement | 12 | 18 |
| 3 | WCF → ASP.NET Core APIs | 18 | 28 |
| 4 | MVC 5 → ASP.NET Core, Windows Services, HTTP | 12 | 22 |
| 5 | Validation, hardening, cut-over | 5 | 12 |
| **Total** | | **55** | **92** |

At a two-developer team working full-time, the calendar range is **12–16 weeks**. With a single developer or shared-time resourcing, the calendar range extends to **18–22 weeks**. These figures assume that stub project removal and test-coverage uplift occur within the phases shown.

---

## 9. Final Recommendation

**Go — with conditions.**

The migration to .NET 8 is technically viable, strategically necessary, and aligned with Microsoft's published support roadmap. Remaining on .NET Framework 4.7.1 is not a safe long-term posture: the credential exposure alone constitutes an immediate security liability, and the inability to containerise the workload blocks cloud-native deployment strategies.

The risk profile is manageable provided the following conditions are met before Phase 3 begins:

1. Credentials are rotated and externalised to Azure Key Vault (Phase 1 gate).
2. A working CI/CD pipeline with automated build and test gates is in place.
3. A WCF service prototype validates the Strangler Fig approach on a non-critical endpoint.

If the team cannot satisfy condition 1 within the first two weeks, migration should pause until that security risk is resolved regardless of other progress.

Subject to those conditions, the recommendation is to **proceed** with the phased migration plan as described, targeting a production cut-over no later than Q4 2026.
