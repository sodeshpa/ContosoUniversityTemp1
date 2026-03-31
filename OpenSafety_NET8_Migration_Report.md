# OpenSafety .NET 8 Migration Report

> **Project:** OpenSafety Solution  
> **Repository:** https://gitlab.rd.loreal/opensafetyAdm/opensafety (branch `master`)  
> **Analysis Date:** 2024  
> **Target Framework:** .NET 8.0  
> **Current Framework:** .NET Framework 4.7.1 / 4.5.2 (Legacy)

---

## Executive Summary

This document provides a comprehensive analysis and migration plan for upgrading the OpenSafety solution from .NET Framework to .NET 8. The solution consists of 18 projects with approximately **78,636 lines of code**, presenting a significant modernization opportunity.

**Key Findings:**
- **18 projects** require framework updates (15 on .NET Framework 4.7.1, 2 on EOL .NET Framework 4.5.2, 1 on EOL .NET Core 3.1)
- **Zero projects** currently target .NET 8
- **225 files (39% of codebase)** reference APIs incompatible with .NET 8
- **22-week estimated timeline** (~92 developer-days, reducible to 12-14 weeks with 2 developers)

---

## Table of Contents

1. [Solution Overview](#1-solution-overview)
2. [Current Technology Stack](#2-current-technology-stack)
3. [Migration Complexity Assessment](#3-migration-complexity-assessment)
4. [Breaking Changes & Incompatibilities](#4-breaking-changes--incompatibilities)
5. [Migration Strategy](#5-migration-strategy)
6. [Detailed Phase Breakdown](#6-detailed-phase-breakdown)
7. [Risk Assessment](#7-risk-assessment)
8. [Effort Estimation](#8-effort-estimation)
9. [Recommendations](#9-recommendations)

---

## 1. Solution Overview

### 1.1 Project Inventory

| # | Project | Type | Framework | Status | Lines |
|---|---|---|---|---|---|
| 1 | OpenSafetyCrossCutting | Library | .NET FW 4.7.1 | ? Active | ~4,200 |
| 2 | OpenSafetyDomainModel | Library | .NET FW 4.7.1 | ? Active | ~3,800 |
| 3 | OpenSafetyContract | Library | .NET FW 4.7.1 | ? Active | ~5,100 |
| 4 | OPenSafetyInfrastructure | Library | .NET FW 4.7.1 | ? Active | ~8,900 |
| 5 | OpenSafetyApplication | Library | .NET FW 4.7.1 | ? Active | ~12,500 |
| 6 | OpenSafetyDependancyResolver | Library | .NET FW 4.7.1 | ? Dissolve into host | ~800 |
| 7 | OpenSafetyDistributedService | WCF Host | .NET FW 4.7.1 | ? Active | ~4,700 |
| 8 | OpenSafetyFrontend | ASP.NET MVC 5 | .NET FW 4.7.1 | ? Active | ~21,400 |
| 9 | WsAsynchronousSilicoState | Windows Service | .NET FW 4.7.1 | ? Active | ~650 |
| 10 | OpenSafetyStateChecker | Windows Service | .NET FW 4.7.1 | ? Empty stub | ~120 |
| 11 | ConsoleTest | Console | .NET FW 4.7.1 | ? Dev tool | ~580 |
| 12 | JsonToSql | Console | .NET Core 3.1 | ? Dev tool | ~320 |
| 13 | OpenSafetyDistributedService.Tests | Test | .NET FW 4.7.1 | ? Minimal tests | ~240 |
| 14 | OpenSafetyFrontend.Tests | Test | .NET FW 4.7.1 | ? Minimal tests | ~180 |
| 15-18 | Stub projects (4) | Various | .NET FW 4.5.2/4.7.1 | ? Remove | ~1,200 |

**Total Active Projects:** 10  
**Total Lines of Code:** ~78,636  
**Estimated Non-Comment Code:** ~65,019 lines

### 1.2 Dependency Graph

```
┌─────────────────────────────────────────────────┐
│  OpenSafetyFrontend (ASP.NET MVC 5)            │
│  • 14 MVC Controllers                           │
│  • 11 Web API 2 Controllers                     │
│  • 119 Razor Views                              │
│  • Bootstrap 3.x, jQuery, jqGrid                │
└─────────────────────────────────────────────────┘
                      ↓ WCF
┌─────────────────────────────────────────────────┐
│  OpenSafetyDistributedService (WCF)            │
│  • 8 REST/JSON Services (.svc files)           │
│  • Windows Authentication                       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  OpenSafetyApplication                         │
│  • 41 Application Service Classes               │
│  • AutoMapper 5.1, log4net 2.0.8               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  OPenSafetyInfrastructure                      │
│  • Entity Framework 6.1.3                       │
│  • NEST/Elasticsearch 6.1.0                     │
│  • 31 Entity Type Configurations                │
│  • 14 EF Migrations                             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Azure SQL Database                             │
└─────────────────────────────────────────────────┘
```

---

## 2. Current Technology Stack

### 2.1 Core Frameworks

| Technology | Current Version | .NET 8 Compatible | Action Required |
|---|---|---|---|
| **ASP.NET MVC** | 5.2.7 (System.Web.Mvc) | ? No | Migrate to ASP.NET Core MVC |
| **ASP.NET Web API** | 2 (System.Web.Http) | ? No | Migrate to ASP.NET Core Web API |
| **WCF (Server)** | Full Framework | ? No | Replace with ASP.NET Core Web API |
| **Entity Framework** | 6.1.3 | ? No | Migrate to EF Core 8 |
| **Windows Services** | ServiceBase | ? No | Migrate to BackgroundService |

### 2.2 Key Dependencies (76 unique packages)

#### Critical Replacements Needed

| Current Package | Version | Replacement | Impact |
|---|---|---|---|
| `EntityFramework` | 6.1.3 | `Microsoft.EntityFrameworkCore` 8.x | **HIGH** - 65 files |
| `NEST` / `Elasticsearch.Net` | 6.1.0 | `Elastic.Clients.Elasticsearch` 8.x | **HIGH** - 2,132 lines |
| `Unity` | 4.0.1 / 5.2.1 / 5.11.6 | Built-in DI | **HIGH** - 8 files |
| `log4net` | 2.0.8 | `Microsoft.Extensions.Logging` + Serilog | **MEDIUM** - 50 files |
| `AutoMapper` | 5.1.1 | `AutoMapper` 13.x | **MEDIUM** - 18 files |
| `System.Runtime.Caching` | Built-in | `IMemoryCache` | **LOW** - 1 file |
| `System.Net.Mail.SmtpClient` | Built-in | `MailKit` | **LOW** - 1 file |

#### Upgrade Required

| Package | Current | Target | Breaking Changes |
|---|---|---|---|
| `Newtonsoft.Json` | 4.5.11 - 12.0.3 (4 versions!) | 13.0.3 | Backward-compatible |
| `ClosedXML` | 0.95.2 | 0.102+ | Some API changes |
| `DocumentFormat.OpenXml` | 2.9.1 / 2.10.1 | 3.1.0 | Namespace changes |
| `bootstrap` | 3.3.7 | 5.3.3 | **CSS breaking changes** |
| `jQuery` | 1.10.2 / 3.3.1 (2 versions) | 3.7.1 | Align versions |
| `FontAwesome` | 4.7.0 | 6.x | Icon name changes |

#### Remove/Replace UI Components

| Component | Usage | Action |
|---|---|---|
| `Trirand.jqGrid` 4.6.0 | 7 views (server-side .NET wrapper) | **Replace with DataTables.js or AG Grid CE** |
| `PagedList.Mvc` 4.5.0 | 1 view | Replace with `X.PagedList.Mvc.Core` |
| `Microsoft.AspNet.Web.Optimization` | Bundling/minification | Replace with LibMan + `UseStaticFiles()` |

### 2.3 UI Layer Statistics

**Razor Views:** 119 total (73 full views, 36 partials, 5 layouts)
- **14,614 total lines** across all views
- **Average 123 lines** per view
- **Zero** Tag Helpers (legacy `@Html.*` syntax only)
- **12+ views** reference WCF proxy namespaces (must update `@model` directives)

**JavaScript Files:** 141 total (15 custom, 126 vendor)
- Key integrations: MarvinJS (chemical sketcher), jqGrid, KnockoutJS, Bootstrap 3

**Controllers:** 33 total
- **14 MVC Controllers** (avg 199 lines) - largest: `AcquisitionController` (1,595 lines)
- **11 Web API 2 Controllers** 
- **8 WCF Service Implementations** (avg 590 lines) - largest: `OpenSafetyAdminWCFService` (1,780 lines)

---

## 3. Migration Complexity Assessment

### 3.1 Code-Level Incompatibilities

| Incompatible API | Files Affected | Complexity |
|---|---|---|
| `System.Web` namespace (entire) | **127 files** | **CRITICAL** |
| `System.ServiceModel` (WCF) | **28 files** | **CRITICAL** |
| `System.Data.Entity` (EF6) | **65 files** | **HIGH** |
| `System.Configuration.ConfigurationManager` | **27 files** | **MEDIUM** |
| `System.ServiceProcess.ServiceBase` | 4 files | **MEDIUM** |
| `HttpContext.Current` | 32 files | **MEDIUM** |
| `Session["key"]` | 29 files | **MEDIUM** |
| `Global.asax` / `HttpApplication` | 5 files | **MEDIUM** |
| EF6 Migrations (14 files + configs) | 29 files | **MEDIUM** |

**Total Affected Files:** 225 (39% of codebase)

### 3.2 Architecture Issues

#### Layer Violations
- ? **Critical:** `OPenSafetyInfrastructure` references `OpenSafetyFrontend` (must break this dependency)

#### God Classes (>1,500 lines)
- `CosmetochemApplicationService.cs` - 2,208 lines
- `WebApiElasticSearch.cs` - 2,132 lines  
- `DataApplicationService.cs` - 1,736 lines
- `OpenSafetyAdminWCFService.svc.cs` - 1,780 lines
- `DicoAdapter.cs` - 1,630 lines
- `AcquisitionApplicationService.cs` - 1,543 lines
- `AcquisitionController.cs` - 1,595 lines

**Recommendation:** Decompose during migration to improve maintainability

#### Dead Code Identified
- **4 stub projects** (WebFrontendTest, OpenSafetyFrontedApplication, Fronted.Tests, WebApiOpenSafety)
- **7 empty `UnityConfig.cs`** copies
- **4 duplicate `FilterConfig.cs`** + **4 duplicate `RouteConfig.cs`**
- **`SimpleJson.cs`** - 2,127 lines (redundant embedded JSON parser)
- **16 files** with `throw new NotImplementedException()`
- **192 files < 20 lines** (empty stubs)
- **OpenSafetyStateChecker** - empty `OnStart`/`OnStop` (never implemented)

**Recommendation:** Remove in Phase 0 (Cleanup) to reduce migration noise

### 3.3 Test Coverage

| Metric | Value | Status |
|---|---|---|
| Test projects | 4 (2 active, 2 empty stubs) | ? Minimal |
| Active test methods | ~3 | ? Critical |
| Commented-out tests | 5+ | ? Unmaintained |
| Mocking framework | None | ? Missing |
| Code coverage | ~0% | ? Critical |

**Recommendation:** Build comprehensive test suite in Phase 6

---

## 4. Breaking Changes & Incompatibilities

### 4.1 WCF to ASP.NET Core Web API

**Current State:**
- 8 WCF REST services using `[WebGet]` / `[WebInvoke]` attributes
- Hosted via `.svc` files in IIS
- 6 WCF client proxies in Frontend + 3 in ConsoleTest

**Migration Required:**
1. Create 8 `[ApiController]` classes to replace WCF services
2. Map `[WebGet(UriTemplate="...")]` ? `[HttpGet("{param}")]`
3. Replace `FaultException` error handling ? `ProblemDetails` + middleware
4. Replace WCF client proxies with typed `HttpClient` via `IHttpClientFactory`
5. Delete all `.svc` files, service references, ASMX proxies

**Risk:** External WCF consumers may break ? **Mitigation:** Strangler Fig pattern (run both in parallel)

### 4.2 Entity Framework 6 to EF Core 8

**Changes Required:**
- Convert 31 `EntityTypeConfiguration<T>` ? `IEntityTypeConfiguration<T>`
- Update `DbContext` constructor to accept `DbContextOptions<T>`
- Delete 14 existing EF6 migration files
- Create new baseline migration via `dotnet ef migrations add InitialCreate`
- Fix 4 instances of `new OpenSafetyDBContext()` ? inject via DI
- Rewrite raw SQL queries to use `FromSqlRaw()` or Dapper

**Risk:** Schema mismatch ? **Mitigation:** Scaffold from production DB to verify before cutover

### 4.3 Dependency Injection: Unity ? Built-in DI

**Current:** Unity IoC container (3 different versions: 4.0.1, 5.2.1, 5.11.6)  
**Target:** `Microsoft.Extensions.DependencyInjection` (built-in)

**Migration:**
- Translate all `container.RegisterType<I, T>()` ? `services.AddScoped<I, T>()`
- Dissolve `OpenSafetyDependancyResolver` project
- Move registrations into `Program.cs` startup

### 4.4 Configuration: App.config/Web.config ? appsettings.json

**Current:** 27 files use `ConfigurationManager.AppSettings["key"]`  
**Target:** `IConfiguration` / `IOptions<T>` pattern

**Changes:**
- Migrate all 13 `Web.config` + 13 `App.config` settings to `appsettings.json`
- Inject `IConfiguration` or `IOptions<T>` via constructor
- Use Azure Key Vault for secrets (remove plaintext passwords)

### 4.5 Session Management

**Current:** `Session["key"]` in 29 files  
**Target:** `ISession.GetString()` / `SetString()` via `IHttpContextAccessor`

### 4.6 Logging: log4net ? Microsoft.Extensions.Logging

**Current:** Static `ILog _log = LogManager.GetLogger(typeof(T))` in 50 files  
**Target:** Inject `ILogger<T>` via constructor + Serilog sink

---

## 5. Migration Strategy

### 5.1 Principles

1. **Bottom-Up Migration** - Start with foundation libraries (no dependencies), work upward
2. **One Project Per Sprint** - Ensure each project compiles independently before moving on
3. **Strangler Fig Pattern** - Deploy new .NET 8 API alongside existing WCF; redirect consumers incrementally
4. **No Big Bang** - Enable partial deployments after Phase 3
5. **Remove Before Replacing** - Delete dead code first (Phase 0) to reduce noise

### 5.2 Target Architecture

```
??????????????????????????????????????????????????????????
?  OpenSafetyFrontend (ASP.NET Core 8 MVC + Razor)      ?
?  � Typed HttpClient ? OpenSafetyDistributedService     ?
?  � IHttpContextAccessor (replaces HttpContext.Current) ?
?  � ISession (replaces Session["key"])                  ?
?  � Windows Authentication (Negotiate/Kerberos)         ?
??????????????????????????????????????????????????????????
                         ? HTTP/JSON
??????????????????????????????????????????????????????????
?  OpenSafetyDistributedService (ASP.NET Core 8 Web API) ?
?  � 8 [ApiController] replacing 8 WCF .svc services    ?
?  � Swashbuckle.AspNetCore (OpenAPI/Swagger UI)        ?
?  � Built-in DI (IServiceCollection) in Program.cs     ?
??????????????????????????????????????????????????????????
                         ?
??????????????????????????????????????????????????????????
?  OpenSafetyApplication (Class Library, net8.0)        ?
?  � Application services + AutoMapper 13 profiles       ?
?  � ILogger<T> (replaces log4net)                       ?
?  � IOptions<T> (replaces ConfigurationManager)         ?
??????????????????????????????????????????????????????????
                         ?
??????????????????????????????????????????????????????????
?  OPenSafetyInfrastructure (Class Library, net8.0)     ?
?  � EF Core 8 DbContext + Migrations                    ?
?  � Elastic.Clients.Elasticsearch 8.x                   ?
?  � IHttpClientFactory-based external API clients       ?
??????????????????????????????????????????????????????????
                         ?
??????????????????????????????????????????????????????????
?  Foundation: OpenSafetyDomainModel / Contract /        ?
?              OpenSafetyCrossCutting (net8.0)           ?
??????????????????????????????????????????????????????????

WsAsynchronousSilicoState ? .NET 8 Worker Service (BackgroundService)
```

---

## 6. Detailed Phase Breakdown

### Phase 0 - Preparation & Cleanup (Week 1 - ~5 days)

**Objectives:**
- Establish migration branch
- Install tooling
- Remove dead code and fix critical violations

**Tasks:**
1. Create migration branch: `git checkout -b feature/dotnet8-migration`
2. Install .NET 8 SDK, `dotnet-ef`, `upgrade-assistant` tools
3. **Fix critical layer violation:** Remove `OpenSafetyFrontend` reference from `OPenSafetyInfrastructure`
4. **Delete 4 stub projects:** WebFrontendTest, OpenSafetyFrontedApplication, Fronted.Tests, WebApiOpenSafety
5. Delete 7 empty `UnityConfig.cs` stubs (keep only real one in DependancyResolver)
6. Delete 4 duplicate `FilterConfig.cs` + 4 duplicate `RouteConfig.cs`
7. Delete `SimpleJson.cs` (2,127 lines - redundant)
8. **Security:** Rotate plaintext credentials in Web.config; add to `.gitignore`
9. Run `upgrade-assistant analyze OpenSafety.sln` and document warnings

**Deliverables:**
- Clean codebase with ~5,000 fewer lines of dead code
- Documented list of all upgrade warnings
- Secured configuration files

---

### Phase 1 - Foundation Libraries (Weeks 2-3 - ~6 days)

**Order:** Bottom-up (no dependencies first)

#### 1.1 OpenSafetyCrossCutting
- Convert to SDK-style `net8.0` csproj
- Replace `log4net` ? `ILogger<T>` abstractions
- Replace `System.Runtime.Caching` ? `IMemoryCache` interface
- Replace `SmtpClient` ? `MailKit` in `OpsEmailSender.cs`
- Fix `GenerateCsvFile` (remove `HttpContext.Current` ? use `IHttpContextAccessor`)
- Upgrade: `ClosedXML` ? 0.102, `DocumentFormat.OpenXml` ? 3.x, `Newtonsoft.Json` ? 13.x
- Remove: `Unity`, `WebActivatorEx`, `System.Web` references

#### 1.2 OpenSafetyDomainModel
- Convert to SDK-style `net8.0` csproj
- Remove dead code: `IRepository`, `DicoDomainSpecification`
- Remove: `Unity`, `Microsoft.AspNet.Mvc`, `Microsoft.CodeDom.Providers`
- Add: `<Nullable>enable</Nullable>`

#### 1.3 OpenSafetyContract
- Convert to SDK-style `net8.0` csproj
- **Strip all WCF attributes** from 9 service interfaces:
  - Remove: `[ServiceContract]`, `[OperationContract]`, `[WebGet]`, `[WebInvoke]`, `[FaultContract]`
- Remove: `System.ServiceModel` reference
- Remove: Unity stub

**Deliverables:**
- 3 projects targeting `net8.0`
- All projects compile with `dotnet build`
- No WCF dependencies remain in Contract layer

---

### Phase 2 - Infrastructure & Application (Weeks 4-8 - ~17 days)

#### 2.1 OPenSafetyInfrastructure (~10 days)

**EF6 ? EF Core 8 Migration:**
1. Convert 31 `EntityTypeConfiguration<T>` ? `IEntityTypeConfiguration<T>`
2. Update `OpenSafetyDBContext`:
   - Add constructor accepting `DbContextOptions<OpenSafetyDBContext>`
   - Override `OnModelCreating()` to apply configurations
3. Delete all 14 EF6 migration files (`.cs`, `.Designer.cs`, `Configuration.cs`)
4. Run `dotnet ef migrations add InitialCreate` for new baseline
5. Fix 4 instances of `new OpenSafetyDBContext()` ? inject via DI
6. Update raw SQL queries to use `FromSqlRaw()` or Dapper

**Elasticsearch Migration:**
1. Replace `NEST` 6.1 ? `Elastic.Clients.Elasticsearch` 8.x
2. **Rewrite `WebApiElasticSearch.cs` (2,132 lines):**
   - Update query DSL syntax
   - Replace `SearchDescriptor<T>` ? `SearchRequest<T>`
   - Update aggregation syntax

**HTTP Clients:**
1. Delete `Web References/MdmWS` (ASMX proxy)
2. Rewrite `WSMdmRepository` using `IHttpClientFactory`
3. Register all HTTP clients in DI container

**Cross-Cutting:**
- Replace `ConfigurationManager` ? `IConfiguration`
- Replace `log4net` ? `ILogger<T>`

#### 2.2 OpenSafetyApplication (~7 days)

1. Convert to SDK-style `net8.0` csproj
2. Replace `ConfigurationManager` ? `IConfiguration` (inject)
3. Replace `log4net` ? `ILogger<T>` (inject)
4. Fix `SecurityService`: replace `HttpContext.Current.Session` ? `IHttpContextAccessor` + `ISession`
5. **AutoMapper 5.1.1 ? 13.x:**
   - Remove `Mapper.Initialize()` static API
   - Create `Profile`-based mapping classes
   - Register via `services.AddAutoMapper()`
6. Remove: `Unity`, `Unity.Mvc5`, `Microsoft.AspNet.Mvc`
7. Merge duplicate `UnauthorizedException.cs`

**Deliverables:**
- Infrastructure and Application layers targeting `net8.0`
- EF Core 8 baseline migration created
- Elasticsearch 8 client integrated
- AutoMapper 13 configured with Profile classes
- All projects compile successfully

---

### Phase 3 - API Host: WCF ? ASP.NET Core Web API (Weeks 9-12 - ~16 days)

**OpenSafetyDistributedService Migration:**

#### 3.1 Dissolve OpenSafetyDependancyResolver
- Translate all `container.RegisterType<I, T>()` ? `services.AddScoped<I, T>()`
- Create DI registration extension methods: `AddInfrastructure()`, `AddApplication()`

#### 3.2 Create ASP.NET Core Web API Project
**File: Program.cs**
```csharp
var builder = WebApplication.CreateBuilder(args);

// DI registrations
builder.Services.AddControllers();
builder.Services.AddSwaggerGen();
builder.Services.AddInfrastructure(builder.Configuration);
builder.Services.AddApplication();

// Windows Authentication
builder.Services.AddAuthentication(NegotiateDefaults.AuthenticationScheme)
    .AddNegotiate();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

#### 3.3 Configuration Migration
1. Create `appsettings.json` and `appsettings.Production.json`
2. Migrate all `Web.config` `<appSettings>` keys
3. Configure Azure Key Vault for secrets

#### 3.4 Create 8 API Controllers (replacing WCF services)

**Example mapping:**

**Before (WCF):**
```csharp
[ServiceContract]
public interface IDicoService
{
    [OperationContract]
    [WebGet(UriTemplate = "GetBlocs")]
    List<BlocDTO> GetBlocs();
}
```

**After (ASP.NET Core):**
```csharp
[ApiController]
[Route("api/[controller]")]
public class DicoController : ControllerBase
{
    [HttpGet("blocs")]
    public ActionResult<List<BlocDTO>> GetBlocs() { ... }
}
```

**8 Controllers to Create:**
1. `DicoController` ? `OpenSafetyDicoWCFService`
2. `AdminController` ? `OpenSafetyAdminWCFService`
3. `AcquisitionController` ? `OpenSafetyAcquisitionWCFService`
4. `DataController` ? `OpenSafetyDataWCFService`
5. `CosmetochemController` ? `OpenSafetyCosmetochemWCFService`
6. `MdmController` ? `OpenSafetyMdmWCFService`
7. `MpnetController` ? `OpenSafetyMpnetWCFService`
8. `SynonymsController` ? `OpenSafetySynonymsWCFService`

#### 3.5 Error Handling
Replace `FaultException` wrapping with:
- `ProblemDetails` standard responses
- Global exception middleware
- Custom exception filters for `UnauthorizedException`

#### 3.6 Delete Legacy Files
- All 8 `.svc` / `.svc.cs` files
- `Global.asax`
- `Web.config` (replace with minimal IIS handler config)
- `App_Start/UnityConfig.cs`

#### 3.7 Testing
- Test all 8 new API endpoints via Swagger UI
- Verify Windows Auth works
- Compare responses with legacy WCF services

**Deliverables:**
- Fully functional ASP.NET Core 8 Web API
- Swagger/OpenAPI documentation
- 8 controllers with feature parity to WCF services
- Deployed alongside existing WCF (Strangler Fig pattern)

---

### Phase 4 - Frontend: MVC 5 ? ASP.NET Core 8 MVC (Weeks 13-19 - ~29 days)

**OpenSafetyFrontend Migration:**

#### 4.1 Project Setup (~2 days)
1. Delete: `Global.asax`, `Web.config`, all `App_Start/` files
2. Create `Program.cs` with full pipeline:
   - MVC + Session + Windows Auth
   - Exception handler middleware
   - Static files
3. Create `appsettings.json` with connection strings, WCF/API endpoints

#### 4.2 Replace WCF Service References with Typed HttpClient (~5 days)

**Before:**
```csharp
var client = new ServiceDico.DicoServiceClient();
var blocs = client.GetBlocs();
```

**After:**
```csharp
public class DicoApiClient
{
    private readonly HttpClient _httpClient;
    public DicoApiClient(HttpClient httpClient) => _httpClient = httpClient;
    
    public async Task<List<BlocDTO>> GetBlocsAsync()
    {
        return await _httpClient.GetFromJsonAsync<List<BlocDTO>>("api/dico/blocs");
    }
}

// In Program.cs:
builder.Services.AddHttpClient<DicoApiClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["ApiBaseUrl"]);
});
```

**6 Typed Clients to Create:**
1. `DicoApiClient`
2. `AdminApiClient`
3. `AcquisitionApiClient`
4. `DataApiClient`
5. `CosmetochemApiClient`
6. `MdmApiClient`

#### 4.3 Update Controllers (~5 days)

**14 MVC Controllers:**
- Change: `System.Web.Mvc.Controller` ? `Microsoft.AspNetCore.Mvc.Controller`
- Fix: All `using` directives
- Replace: `HttpContext.Current` (32 files) ? inject `IHttpContextAccessor`
- Replace: `Session["key"]` (29 files) ? `ISession.GetString()` / `SetString()`
- Replace: `ConfigurationManager` ? `IConfiguration`
- Update: All WCF proxy calls ? typed `HttpClient` calls (make async)

**11 Web API 2 Controllers:**
- Change: `ApiController` ? `ControllerBase`
- Add: `[ApiController]` attribute
- Change: Return types to `ActionResult<T>`
- Fix: All routing attributes

#### 4.4 Static HttpContext Replacement (~3 days)

**Pattern:**
```csharp
// Before:
var user = HttpContext.Current.Session["User"];

// After:
private readonly IHttpContextAccessor _httpContextAccessor;
var user = _httpContextAccessor.HttpContext.Session.GetString("User");
```

**Files to update:** 32 files with `HttpContext.Current`

#### 4.5 Update 119 Razor Views (~5 days)

**Changes per view:**
1. Update `@model` types (WCF proxy DTOs ? Contract DTOs)
   - Example: `@model OpenSafetyFrontend.ServiceAdmin.BlocDTO` ? `@model OpenSafetyContract.BlocDTO`
2. Update `using` directives:
   - `System.Web.Mvc.Html` ? `Microsoft.AspNetCore.Mvc.Rendering`
3. Keep `@Html.*` helpers (compatible with ASP.NET Core)
4. Update `Ajax.BeginForm` (ensure `Microsoft.jQuery.Unobtrusive.Ajax` package is added)

**12+ views with WCF proxy references to fix**

#### 4.6 Static Asset Management (~2 days)

**Replace Bundle Config with LibMan:**

**Before (Web.Optimization):**
```csharp
bundles.Add(new ScriptBundle("~/bundles/jquery").Include(
    "~/Scripts/jquery-{version}.js"));
```

**After (libman.json):**
```json
{
  "version": "1.0",
  "defaultProvider": "cdnjs",
  "libraries": [
    {
      "library": "jquery@3.7.1",
      "destination": "wwwroot/lib/jquery/"
    }
  ]
}
```

#### 4.7 Replace jqGrid (~3 days)

**7 views using `Trirand.jqGrid` ? migrate to DataTables.js:**

**Before:**
```csharp
@Html.Trirand().JQGrid(Model.BlocsGrid, "grid")
```

**After:**
```html
<table id="blocsTable" class="table table-striped">
  <thead>...</thead>
  <tbody>...</tbody>
</table>

<script>
$('#blocsTable').DataTable({
  ajax: '/api/blocs',
  columns: [...]
});
</script>
```

#### 4.8 Replace Dependencies (~2 days)

| Action | Package | Files |
|---|---|---|
| Replace | `PagedList.Mvc` ? `X.PagedList.Mvc.Core` | 1 |
| Replace | `RestHelper` static methods ? `IHttpClientFactory` | 8 |
| Replace | `log4net` ? `ILogger<T>` | 50 |
| Remove | `System.Web.Optimization` | 8 |

#### 4.9 Bootstrap 3 ? 5 Upgrade (~2 days)

**37+ views with Bootstrap 3 CSS classes:**
- `panel-*` ? `card-*`
- `glyphicon-*` ? FontAwesome 6 or Bootstrap Icons
- `col-xs-*` ? `col-*` (XS removed in Bootstrap 5)

**Deliverables:**
- Fully functional ASP.NET Core 8 MVC application
- All 119 views rendering correctly
- Windows Authentication working
- Session state functional
- All static assets loading via LibMan
- DataTables.js replacing jqGrid

---

### Phase 5 - Background Services & Utilities (Week 20 - ~6 days)

#### 5.1 WsAsynchronousSilicoState (~3 days)

**Windows Service ? Worker Service:**

**Before:**
```csharp
public partial class WsAsynchronousSilicoState : ServiceBase
{
    private System.Timers.Timer timer;
    protected override void OnStart(string[] args)
    {
        timer = new Timer(30000);
        timer.Elapsed += Timer_Elapsed;
        timer.Start();
    }
}
```

**After:**
```csharp
public class SilicoStateWorker : BackgroundService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ILogger<SilicoStateWorker> _logger;
    
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromSeconds(30));
        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            await AnalyzeSilicoStateAsync();
        }
    }
}

// Program.cs:
var builder = Host.CreateApplicationBuilder(args);
builder.Services.AddWindowsService();
builder.Services.AddHostedService<SilicoStateWorker>();
```

**Changes:**
1. Replace `ServiceBase` ? `BackgroundService`
2. Replace `System.Timers.Timer` ? `PeriodicTimer`
3. Convert 10 blocking `.Result` calls ? `async`/`await`
4. Inject `IHttpClientFactory` for WCF/API calls
5. Delete `ProjectInstaller.Designer.cs` / `.resx`

#### 5.2 OpenSafetyStateChecker (~1 day)
- Same pattern as 5.1
- **Decision required:** Implement actual logic or retire project (currently empty stub)

#### 5.3 JsonToSql (~1 day)
- Bump `netcoreapp3.1` ? `net8.0`
- Replace `Microsoft.Office.Interop.Excel` ? `ClosedXML` (if used)

#### 5.4 ConsoleTest (~1 day)
- Remove: `System.Runtime.Remoting`, `JavaScriptSerializer`, `WebRequest`
- Replace with `HttpClient`
- **Decision required:** Retire or keep as dev tool

**Deliverables:**
- 2 Windows Services migrated to .NET 8 Worker Services
- Services deployable via `sc.exe create` or Windows Service Manager
- Utilities updated to .NET 8

---

### Phase 6 - Test Modernization (Week 21 - ~9 days)

#### 6.1 Test Infrastructure Setup (~2 days)
- Convert projects to xUnit
- Add `Microsoft.AspNetCore.Mvc.Testing` (WebApplicationFactory)
- Add `Moq` for mocking
- Add `FluentAssertions` for readable assertions

#### 6.2 API Integration Tests (~3 days)

**Example:**
```csharp
public class DicoControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    
    [Fact]
    public async Task GetBlocs_ReturnsSuccessStatusCode()
    {
        var response = await _client.GetAsync("/api/dico/blocs");
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        
        var blocs = await response.Content.ReadFromJsonAsync<List<BlocDTO>>();
        blocs.Should().NotBeEmpty();
    }
}
```

**Coverage:**
- Integration tests for all 8 API controllers
- Test success paths, error handling, auth

#### 6.3 Unit Tests (~3 days)

**Key Classes to Test:**
- `DicoApplicationService`
- `SecurityService`
- `EFDicoRepository`
- `CacheManager`
- AutoMapper profiles

**Mock external dependencies:**
```csharp
var mockRepo = new Mock<IDicoRepository>();
mockRepo.Setup(r => r.GetBlocs()).Returns(TestData.Blocs);

var service = new DicoApplicationService(mockRepo.Object, mockLogger.Object);
var result = service.GetAllBlocs();
result.Should().HaveCount(3);
```

#### 6.4 CI Code Coverage Gate (~1 day)
- Configure code coverage collection in Jenkins
- Set threshold: **?60% coverage** for new code
- Fail build if coverage drops

**Deliverables:**
- Comprehensive test suite (integration + unit)
- ?60% code coverage
- CI/CD pipeline enforcing coverage gate

---

### Phase 7 - CI/CD & Deployment (Week 22 - ~4 days)

#### 7.1 Update Jenkins Pipelines (~2 days)

**Before (MSBuild):**
```groovy
bat "MSBuild.exe OpenSafety.sln /p:Configuration=Release"
```

**After (.NET CLI):**
```groovy
bat "dotnet restore OpenSafety.sln"
bat "dotnet build OpenSafety.sln -c Release --no-restore"
bat "dotnet test OpenSafety.sln -c Release --no-build --logger trx"
bat "dotnet publish OpenSafetyFrontend\\OpenSafetyFrontend.csproj -c Release -o ./publish/frontend"
bat "dotnet publish OpenSafetyDistributedService\\OpenSafetyDistributedService.csproj -c Release -o ./publish/api"
```

**Add EF Migrations:**
```groovy
bat "dotnet ef database update --project OPenSafetyInfrastructure --startup-project OpenSafetyDistributedService"
```

#### 7.2 IIS Configuration (~1 day)

**Prerequisites:**
1. Install **.NET 8 Windows Hosting Bundle** on all IIS servers (dev, pit, int, prod)
   - Download: https://dotnet.microsoft.com/download/dotnet/8.0
2. Configure Application Pools:
   - **.NET CLR Version:** No Managed Code
   - **Pipeline Mode:** Integrated

**web.config for ASP.NET Core:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="aspNetCore" path="*" verb="*" modules="AspNetCoreModuleV2" resourceType="Unspecified" />
    </handlers>
    <aspNetCore processPath="dotnet" 
                arguments=".\OpenSafetyFrontend.dll" 
                stdoutLogEnabled="true" 
                stdoutLogFile=".\logs\stdout" 
                hostingModel="inprocess" />
  </system.webServer>
</configuration>
```

#### 7.3 Deployment Strategy (~1 day)

**Strangler Fig Pattern:**
1. Deploy new ASP.NET Core API to `/api-v2` endpoint
2. Update Frontend to call `/api-v2` instead of WCF endpoints
3. Monitor both systems in parallel for 2 weeks
4. Gradually redirect external WCF consumers to new API
5. Decommission WCF services once all consumers migrated

**Rollback Plan:**
- Keep WCF services running during transition
- Feature flag in Frontend to switch between WCF/API
- Database schema must support both (no breaking changes)

**Deliverables:**
- Updated Jenkins pipelines using `dotnet` CLI
- IIS servers configured with .NET 8 Hosting Bundle
- Deployment runbook documenting Strangler Fig cutover
- Rollback procedures tested

---

## 7. Risk Assessment

### 7.1 Critical Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **External WCF consumers break during cutover** | ? HIGH | ?? CRITICAL | **Strangler Fig pattern** - Run WCF and new REST API in parallel; audit all external callers; coordinate migration; maintain backward-compatible API contracts |
| **Elasticsearch cluster version mismatch** (cluster on 6.x, client requires 8.x) | ? HIGH | ?? HIGH | **Pre-migration:** Upgrade ES cluster to 8.x first; OR use NEST 7.x as intermediate step; Test all queries against new cluster before .NET 8 deployment |
| **EF Core migration generates incorrect schema** | ? MEDIUM | ?? HIGH | Run `dotnet ef dbcontext scaffold` on production DB to verify schema; Compare output against current DB schema; Test migrations on production copy before cutover |
| **`Trirand.jqGrid` replacement requires UI redesign** | ? HIGH | ?? MEDIUM | **No drop-in replacement exists** - Dedicate UI sprint to DataTables.js migration; Define feature parity list with stakeholders upfront; Budget 3 days for 7 affected views |
| **AutoMapper 5?13 breaks unmapped properties** | ? HIGH | ?? MEDIUM | Run `cfg.AssertConfigurationIsValid()` in startup tests; Fix all mapping gaps before deployment; Add unit tests for all mapping profiles |

### 7.2 Medium Risks

| Risk | Mitigation |
|---|---|
| **Session state compatibility** (ASP.NET ? ASP.NET Core) | Use distributed cache (Redis) for session state to ensure consistency; Test session behavior across app pool recycling |
| **Windows Auth configuration** (Kerberos/NTLM) | Test negotiate auth in all environments (dev/pit/int/prod); Ensure SPN configured correctly for service account |
| **Large controllers (1,500+ lines) introduce bugs during refactoring** | Decompose incrementally; Write characterization tests before splitting; Review PRs thoroughly |
| **Async/await introduction causes deadlocks** | Avoid `.Result` / `.Wait()`; Use `ConfigureAwait(false)` in library code; Test under load |
| **3rd-party package breaking changes** (Bootstrap 3?5, ClosedXML, etc.) | Allocate dedicated sprints for UI updates; Test all views in browser after Bootstrap upgrade |

### 7.3 Low Risks

| Risk | Mitigation |
|---|---|
| Log4net?Serilog logging gaps | Configure Serilog sinks early; Test log output in all environments |
| Configuration secrets exposure | Use Azure Key Vault; Never commit `appsettings.Production.json`; Rotate all credentials during Phase 0 |

---

## 8. Effort Estimation

### 8.1 Phase Summary

| Phase | Description | Duration | Effort (days) | Resources |
|---|---|---|---|---|
| 0 | Preparation, cleanup, credential rotation | Week 1 | 5 | 1 dev |
| 1 | Foundation libraries (3 projects) | Weeks 2-3 | 6 | 1 dev |
| 2 | Infrastructure (EF Core 8, ES 8) + Application | Weeks 4-8 | 17 | 1-2 devs |
| 3 | WCF ? ASP.NET Core Web API (8 services) | Weeks 9-12 | 16 | 1-2 devs |
| 4 | Frontend MVC 5 ? ASP.NET Core 8 MVC | Weeks 13-19 | 29 | 2 devs |
| 5 | Background services + utilities | Week 20 | 6 | 1 dev |
| 6 | Test modernization (xUnit, Moq, coverage) | Week 21 | 9 | 1-2 devs |
| 7 | CI/CD pipeline + IIS deployment | Week 22 | 4 | 1 dev + DevOps |
| **Total** | | **~22 weeks** | **~92 days** | **1-2 devs** |

### 8.2 Optimization Scenarios

**Single Developer (Sequential):**
- **Duration:** 22 weeks (5.5 months)
- **Risk:** Longer timeline, knowledge concentration

**Two Developers (Parallel):**
- **Duration:** 12-14 weeks (3-3.5 months)
- **Workload Split:**
  - **Dev 1:** Phases 0-3 (Infrastructure, Application, API)
  - **Dev 2:** Phase 4 (Frontend MVC)
  - **Both:** Phases 6-7 (Tests, Deployment)

**Recommended:** **2-developer parallel approach** for 12-14 week delivery

### 8.3 Contingency

- Add **20% buffer** for unforeseen issues: **+18 days**
- **Total with contingency:** ~110 days (22 weeks ? 26 weeks for 1 dev, 14 weeks ? 17 weeks for 2 devs)

---

## 9. Recommendations

### 9.1 Immediate Actions (Pre-Migration)

1. **Rotate all credentials** in Web.config (plaintext passwords found)
2. **Upgrade Elasticsearch cluster** from 6.x to 8.x (if in use)
3. **Audit external WCF consumers** - identify all systems calling OpenSafetyDistributedService
4. **Set up .NET 8 development environment** for all team members
5. **Create migration branch** with branch protection rules

### 9.2 Architecture Improvements

1. **Decompose God Classes** during migration:
   - `CosmetochemApplicationService` (2,208 lines) ? 3-4 focused services
   - `WebApiElasticSearch` (2,132 lines) ? separate query builders
   - `AcquisitionController` (1,595 lines) ? 3 controllers
2. **Fix layer violation:** Remove Frontend dependency from Infrastructure
3. **Enable nullable reference types** globally (`<Nullable>enable</Nullable>`)
4. **Introduce async/await** systematically (currently <1% of codebase)

### 9.3 Post-Migration Modernization

**Phase 8+ (Future Enhancements):**
- Migrate from MVC Razor views ? **Blazor Server** or **React SPA**
- Containerize all services ? **Docker + Kubernetes**
- Implement **CQRS + MediatR** pattern for complex workflows
- Add **OpenTelemetry** for distributed tracing
- Upgrade from Bootstrap 5 ? modern component library (e.g., MudBlazor, Radzen)

### 9.4 Success Criteria

**Definition of Done:**
- ? All 10 active projects target `net8.0`
- ? All 225 incompatible API usages replaced
- ? ?60% code coverage with automated tests
- ? CI/CD pipeline using `dotnet` CLI
- ? Successfully deployed to production with zero downtime
- ? All external WCF consumers migrated to new API
- ? Performance benchmarks meet or exceed legacy system
- ? Security audit passed (no plaintext credentials, Azure Key Vault configured)

---

## Appendix A: Key Contacts & Resources

**Project Stakeholders:**
- **Technical Lead:** [Name]
- **Product Owner:** [Name]
- **DevOps:** [Name]

**Resources:**
- **.NET 8 Migration Guide:** https://learn.microsoft.com/en-us/aspnet/core/migration/
- **EF Core 8 Migration:** https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-8.0/
- **WCF to ASP.NET Core:** https://learn.microsoft.com/en-us/aspnet/core/grpc/wcf
- **Upgrade Assistant Tool:** https://dotnet.microsoft.com/platform/upgrade-assistant

---

## Document Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2024 | Upgrade Assistant | Initial comprehensive analysis and migration plan |

---

**End of Report**
