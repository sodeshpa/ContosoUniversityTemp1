# OpenSafety .NET 8 Upgrade Report

**Report Date:** 2024  
**Project:** OpenSafety Solution  
**Repository:** https://gitlab.rd.loreal/opensafetyAdm/opensafety  
**Target Framework:** .NET 8.0  
**Report Type:** Upgrade Assessment & Execution Summary

---

## Executive Summary

This report provides a comprehensive upgrade assessment for migrating the OpenSafety solution from .NET Framework 4.7.1/4.5.2 to .NET 8.0. The solution consists of 18 projects with approximately **78,636 lines of code** across multiple architectural layers.

### Key Statistics

| Metric | Value |
|--------|-------|
| **Total Projects** | 18 (10 active, 4 stub, 2 dev tools, 2 test) |
| **Lines of Code** | ~78,636 total (~65,019 non-comment) |
| **Current Frameworks** | .NET Framework 4.7.1 (15 projects), 4.5.2 (2 projects), .NET Core 3.1 (1 project) |
| **Target Framework** | .NET 8.0 |
| **Estimated Effort** | 92 developer-days (22 weeks single dev, 12-14 weeks with 2 devs) |
| **Complexity Level** | **HIGH** - 225 files (39%) contain .NET 8 incompatible APIs |

### Upgrade Status

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 0: Preparation & Cleanup | ? Not Started | 0% |
| Phase 1: Foundation Libraries | ? Not Started | 0% |
| Phase 2: Infrastructure & Application | ? Not Started | 0% |
| Phase 3: API Migration (WCF ? Web API) | ? Not Started | 0% |
| Phase 4: Frontend Migration (MVC 5 ? Core) | ? Not Started | 0% |
| Phase 5: Background Services | ? Not Started | 0% |
| Phase 6: Test Modernization | ? Not Started | 0% |
| Phase 7: CI/CD & Deployment | ? Not Started | 0% |
| **Overall Progress** | **? Not Started** | **0%** |

---

## 1. Solution Architecture Overview

### 1.1 Project Distribution

```
???????????????????????????????????????????????????????????????
?                     PRESENTATION LAYER                       ?
???????????????????????????????????????????????????????????????
? OpenSafetyFrontend (ASP.NET MVC 5 + Web API 2)             ?
? - 119 Razor views (14,614 lines)                            ?
? - 14 MVC Controllers + 11 API Controllers                   ?
? - 6 WCF Service Reference proxies                           ?
???????????????????????????????????????????????????????????????
? OpenSafetyDistributedService (WCF REST Services)            ?
? - 8 WCF .svc services                                       ?
? - JSON/REST over webHttpBinding                             ?
???????????????????????????????????????????????????????????????
                              ?
???????????????????????????????????????????????????????????????
?                      BUSINESS LAYER                          ?
???????????????????????????????????????????????????????????????
? OpenSafetyApplication (Application Services)                ?
? - 41 application service classes                            ?
? - AutoMapper 5.1.1 (static API - obsolete)                  ?
? - 13 adapter classes                                         ?
???????????????????????????????????????????????????????????????
                              ?
???????????????????????????????????????????????????????????????
?                       DATA LAYER                             ?
???????????????????????????????????????????????????????????????
? OPenSafetyInfrastructure                                    ?
? - Entity Framework 6.1.3 (65 files)                         ?
? - Elasticsearch NEST 6.1.0 (deprecated)                     ?
? - 31 EntityTypeConfiguration classes                        ?
? - 14 EF6 migrations                                          ?
???????????????????????????????????????????????????????????????
                              ?
???????????????????????????????????????????????????????????????
?                     FOUNDATION LAYER                         ?
???????????????????????????????????????????????????????????????
? OpenSafetyDomainModel (Entities + Interfaces)               ?
? OpenSafetyContract (DTOs + Service Interfaces)              ?
? OpenSafetyCrossCutting (Utilities + Helpers)                ?
???????????????????????????????????????????????????????????????

???????????????????????????????????????????????????????????????
?                    BACKGROUND SERVICES                       ?
???????????????????????????????????????????????????????????????
? WsAsynchronousSilicoState (Windows Service)                 ?
? - 30-second polling timer                                    ?
? - Calls WCF endpoint for silico analysis                    ?
???????????????????????????????????????????????????????????????
```

### 1.2 Key Technologies in Use

| Category | Technology | Version | Status |
|----------|-----------|---------|--------|
| **Web Framework** | ASP.NET MVC | 5.2.7 | ? Must replace |
| **Web API** | ASP.NET Web API | 2.0 | ? Must replace |
| **Services** | WCF (REST/JSON) | Full Framework | ? Must replace |
| **ORM** | Entity Framework | 6.1.3 | ? Must replace |
| **Search** | Elasticsearch NEST | 6.1.0 | ? Must replace |
| **IoC Container** | Unity | 4.0.1 / 5.2.1 / 5.11.6 | ? Must replace |
| **Logging** | log4net | 2.0.8 | ? Should replace |
| **Mapping** | AutoMapper | 5.1.1 | ? Must upgrade |
| **UI Framework** | Bootstrap | 3.3.7 | ? Should upgrade |
| **Grid Component** | Trirand.jqGrid | 4.6.0 | ? Must replace |

---

## 2. Upgrade Complexity Analysis

### 2.1 Breaking Changes by Category

#### ?? CRITICAL - Complete Replacement Required

| API / Framework | Files Affected | Reason | Replacement |
|----------------|----------------|--------|-------------|
| **System.Web** | 127 files | Not available in .NET Core | ASP.NET Core APIs |
| **System.ServiceModel (WCF)** | 28 files | Server hosting not supported | ASP.NET Core Web API |
| **System.Data.Entity (EF6)** | 65 files | Not ported to .NET Core | EF Core 8.x |
| **System.ServiceProcess** | 4 files | Not available | BackgroundService |

#### ?? HIGH - Major Refactoring Required

| API / Framework | Files Affected | Reason | Replacement |
|----------------|----------------|--------|-------------|
| **Unity IoC** | 8 files | Unmaintained, not idiomatic | Built-in DI |
| **NEST 6.x** | 2 files (2,132 lines) | Deprecated, ES 6.x EOL | Elastic.Clients.Elasticsearch 8.x |
| **AutoMapper 5.x** | 18 files | Static API removed | AutoMapper 13.x |
| **System.Configuration** | 27 files | Not default in .NET Core | IConfiguration / IOptions<T> |

#### ?? MEDIUM - Upgrade/Minor Changes

| API / Framework | Files Affected | Action |
|----------------|----------------|--------|
| **log4net** | 50 files | Replace with ILogger<T> + Serilog |
| **HttpContext.Current** | 32 files | Inject IHttpContextAccessor |
| **Session["key"]** | 29 files | Use ISession.GetString/SetString |
| **Trirand.jqGrid** | 7 views | Migrate to DataTables.js |
| **Bootstrap 3** | 37+ views | Upgrade to Bootstrap 5 |

### 2.2 Incompatibility Summary

```
Total C# Files: 578
?? .NET 8 Compatible: 353 files (61%)
?? Requires Changes: 225 files (39%)
   ?? System.Web dependencies: 127 files
   ?? EF6 dependencies: 65 files
   ?? WCF dependencies: 28 files
   ?? log4net: 50 files
   ?? HttpContext.Current: 32 files
   ?? Session access: 29 files
   ?? ConfigurationManager: 27 files
   
   (Note: Files may have multiple issues)
```

### 2.3 Dead Code Identified (Cleanup Opportunity)

| Category | Count | Action |
|----------|-------|--------|
| **Stub Projects** | 4 projects | Delete entirely |
| **Empty UnityConfig.cs** | 7 copies | Delete (keep 1 real) |
| **Duplicate FilterConfig.cs** | 4 copies | Delete all |
| **Duplicate RouteConfig.cs** | 4 copies | Delete all |
| **SimpleJson.cs** | 1 file (2,127 lines) | Delete (redundant) |
| **NotImplementedException** | 16 files | Review & implement or delete |
| **Empty stub files (<20 lines)** | 192 files | Review & consolidate |
| **Total Removable Code** | ~5,000-6,000 lines | Clean in Phase 0 |

---

## 3. Detailed Upgrade Roadmap

### Phase 0: Preparation & Cleanup (Week 1 - 5 days)

**Objectives:**
- ? Establish clean migration baseline
- ? Remove dead code and security issues
- ? Fix architectural violations

**Tasks:**
1. Create migration branch: `feature/dotnet8-migration`
2. Install tooling: .NET 8 SDK, `dotnet-ef`, `upgrade-assistant`
3. **Security**: Rotate plaintext credentials in Web.config (found in WCF service)
4. **Fix layer violation**: Remove `OpenSafetyFrontend` dependency from `OPenSafetyInfrastructure`
5. Delete 4 stub projects (WebFrontendTest, OpenSafetyFrontedApplication, Fronted.Tests, WebApiOpenSafety)
6. Delete 7 empty `UnityConfig.cs` stubs + 8 duplicate config files
7. Delete `SimpleJson.cs` (2,127 lines - superseded by Newtonsoft.Json)
8. Run `upgrade-assistant analyze OpenSafety.sln` and document all warnings

**Deliverables:**
- Clean codebase with ~5,000 fewer LOC
- Security issues resolved
- Documented analysis report

---

### Phase 1: Foundation Libraries (Weeks 2-3 - 6 days)

**Scope:** 3 projects with zero external dependencies

#### 1.1 OpenSafetyCrossCutting (2 days)
- ? Convert to SDK-style .csproj targeting `net8.0`
- ? Replace `System.Runtime.Caching` ? `IMemoryCache` interface
- ? Replace `System.Net.Mail.SmtpClient` ? `MailKit`
- ? Fix `GenerateCsvFile` (remove `HttpContext.Current`)
- ? Upgrade: ClosedXML (0.95 ? 0.102), DocumentFormat.OpenXml (2.9 ? 3.1), Newtonsoft.Json (4.5-12.0 ? 13.0)
- ? Remove: Unity, WebActivatorEx, System.Web references

#### 1.2 OpenSafetyDomainModel (2 days)
- ? Convert to SDK-style .csproj targeting `net8.0`
- ? Remove dead interfaces: `IRepository<T>`, `DicoDomainSpecification`
- ? Add nullable reference types: `<Nullable>enable</Nullable>`
- ? Remove: Unity, Microsoft.AspNet.Mvc, Microsoft.CodeDom.Providers

#### 1.3 OpenSafetyContract (2 days)
- ? Convert to SDK-style .csproj targeting `net8.0`
- ? **Strip all WCF attributes** from 9 service interfaces:
  - Remove: `[ServiceContract]`, `[OperationContract]`, `[WebGet]`, `[WebInvoke]`, `[FaultContract]`
- ? Remove: `System.ServiceModel`, Unity references
- ? Preserve: 93 DTO classes (remain POCO - no changes needed)

**Success Criteria:**
- All 3 projects compile with `dotnet build`
- Zero .NET Framework dependencies
- Zero WCF dependencies in Contract layer

---

### Phase 2: Infrastructure & Application (Weeks 4-8 - 17 days)

#### 2.1 OPenSafetyInfrastructure (10 days)

**EF6 ? EF Core 8 Migration:**
1. ? Convert 31 `EntityTypeConfiguration<T>` ? `IEntityTypeConfiguration<T>`
2. ? Update `OpenSafetyDBContext`:
   - Add constructor: `public OpenSafetyDBContext(DbContextOptions<OpenSafetyDBContext> options) : base(options)`
   - Update `OnModelCreating()` to apply configurations
3. ? Delete all 14 EF6 migration files (`.cs`, `.Designer.cs`, `Configuration.cs`)
4. ? Create new baseline migration: `dotnet ef migrations add InitialCreate`
5. ? Fix 4 instances of `new OpenSafetyDBContext()` ? inject via DI
6. ? Update raw SQL queries: use `FromSqlRaw()` or consider Dapper

**Elasticsearch Migration:**
1. ? Replace NEST 6.1.0 ? `Elastic.Clients.Elasticsearch` 8.x
2. ? **Rewrite `WebApiElasticSearch.cs` (2,132 lines)**:
   - Update query DSL syntax
   - Replace `SearchDescriptor<T>` ? `SearchRequest<T>`
   - Update aggregation builders
   - Test all search queries

**HTTP Clients:**
1. ? Delete ASMX Web Reference: `Web References/MdmWS`
2. ? Rewrite `WSMdmRepository` using `IHttpClientFactory`
3. ? Register typed HTTP clients in DI

**Cross-Cutting:**
- ? Replace `ConfigurationManager` ? `IConfiguration` (inject)
- ? Replace `log4net` ? `ILogger<T>` (inject)

#### 2.2 OpenSafetyApplication (7 days)

1. ? Convert to SDK-style .csproj targeting `net8.0`
2. ? Replace `ConfigurationManager` ? `IConfiguration` (27 instances)
3. ? Replace `log4net` ? `ILogger<T>` (50 instances)
4. ? Fix `SecurityService`: `HttpContext.Current.Session` ? `IHttpContextAccessor` + `ISession`
5. ? **AutoMapper 5.1.1 ? 13.x**:
   - Remove `Mapper.Initialize()` static API
   - Create `Profile` classes for all mappings
   - Register: `services.AddAutoMapper(typeof(MappingProfile).Assembly)`
6. ? Remove: Unity, Unity.Mvc5, Microsoft.AspNet.Mvc
7. ? Merge duplicate `UnauthorizedException.cs` (remove from Application, keep in CrossCutting)

**Success Criteria:**
- Infrastructure and Application layers compile on `net8.0`
- EF Core 8 migrations successfully generated
- All dependencies injected via constructor (no `new DbContext()`)

---

### Phase 3: API Migration - WCF ? ASP.NET Core Web API (Weeks 9-12 - 16 days)

**Scope:** Replace 8 WCF services with ASP.NET Core Web API controllers

#### 3.1 Dissolve OpenSafetyDependancyResolver (2 days)
- ? Translate all Unity `container.RegisterType<I,T>()` ? `services.AddScoped<I,T>()`
- ? Create extension methods: `AddInfrastructure()`, `AddApplication()`
- ? Delete project after migration complete

#### 3.2 Create ASP.NET Core Web API Project (3 days)

**New `Program.cs`:**
```csharp
var builder = WebApplication.CreateBuilder(args);

// Services
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// DI
builder.Services.AddInfrastructure(builder.Configuration);
builder.Services.AddApplication();

// Windows Authentication
builder.Services.AddAuthentication(NegotiateDefaults.AuthenticationScheme)
    .AddNegotiate();
builder.Services.AddAuthorization();

var app = builder.Build();

// Middleware
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

**New `appsettings.json`:**
```json
{
  "ConnectionStrings": {
    "OpenSafetyDB": "..."
  },
  "Elasticsearch": {
    "Url": "http://elasticsearch:9200"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  }
}
```

#### 3.3 Create 8 API Controllers (8 days)

| WCF Service | New Controller | Key Endpoints | LOC |
|-------------|----------------|---------------|-----|
| `OpenSafetyDicoWCFService` | `DicoController` | GetBlocs, GetSources, GetMetas | ~1,006 |
| `OpenSafetyAdminWCFService` | `AdminController` | CRUD for admin entities | ~1,780 |
| `OpenSafetyAcquisitionWCFService` | `AcquisitionController` | Acquisition management | ~520 |
| `OpenSafetyDataWCFService` | `DataController` | Elasticsearch queries | ~880 |
| `OpenSafetyCosmetochemWCFService` | `CosmetochemController` | Cosmetochem API proxy | ~450 |
| `OpenSafetyMdmWCFService` | `MdmController` | MDM integration | ~310 |
| `OpenSafetyMpnetWCFService` | `MpnetController` | MPnet API proxy | ~270 |
| `OpenSafetySynonymsWCFService` | `SynonymsController` | Synonym lookup | ~230 |

**Migration Pattern:**

**Before (WCF):**
```csharp
[ServiceContract]
public interface IDicoService
{
    [OperationContract]
    [WebGet(UriTemplate = "GetBlocs", ResponseFormat = WebMessageFormat.Json)]
    List<BlocDTO> GetBlocs();
}

public class OpenSafetyDicoWCFService : IDicoService
{
    public List<BlocDTO> GetBlocs()
    {
        var service = new DicoApplicationService();
        return service.GetAllBlocs();
    }
}
```

**After (ASP.NET Core):**
```csharp
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class DicoController : ControllerBase
{
    private readonly IDicoApplicationService _dicoService;
    private readonly ILogger<DicoController> _logger;

    public DicoController(IDicoApplicationService dicoService, ILogger<DicoController> logger)
    {
        _dicoService = dicoService;
        _logger = logger;
    }

    [HttpGet("blocs")]
    [ProducesResponseType(typeof(List<BlocDTO>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<List<BlocDTO>>> GetBlocs()
    {
        try
        {
            var blocs = await _dicoService.GetAllBlocsAsync();
            return Ok(blocs);
        }
        catch (UnauthorizedException ex)
        {
            _logger.LogWarning(ex, "Unauthorized access to GetBlocs");
            return Unauthorized();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving blocs");
            return StatusCode(500, new ProblemDetails 
            { 
                Title = "Internal Server Error",
                Detail = ex.Message 
            });
        }
    }
}
```

#### 3.4 Error Handling (1 day)
- ? Replace `FaultException` ? `ProblemDetails` + HTTP status codes
- ? Create global exception middleware
- ? Custom exception filter for `UnauthorizedException` ? 401

#### 3.5 Delete Legacy Files (1 day)
- ? Delete 8 `.svc` + `.svc.cs` files
- ? Delete `Global.asax`
- ? Delete `Web.config` (replace with minimal IIS handler config)
- ? Delete `App_Start/UnityConfig.cs`

#### 3.6 Testing & Validation (1 day)
- ? Test all 8 controllers via Swagger UI
- ? Verify Windows Auth (Negotiate) works
- ? Compare JSON responses with legacy WCF services
- ? Load test critical endpoints

**Success Criteria:**
- 8 functional ASP.NET Core Web API controllers
- Swagger/OpenAPI documentation accessible
- Feature parity with WCF services
- Deployed to test environment (alongside existing WCF)

---

### Phase 4: Frontend Migration - MVC 5 ? ASP.NET Core 8 (Weeks 13-19 - 29 days)

**Scope:** Migrate ASP.NET MVC 5 + Web API 2 frontend to ASP.NET Core 8 MVC

#### 4.1 Project Setup (2 days)
1. ? Delete: `Global.asax`, `Web.config`, all `App_Start/` files
2. ? Create new `Program.cs`:
```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews();
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});

// Typed HTTP clients
builder.Services.AddHttpClient<DicoApiClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["ApiBaseUrl"]);
});
// ... register 5 more clients

builder.Services.AddAuthentication(NegotiateDefaults.AuthenticationScheme)
    .AddNegotiate();

var app = builder.Build();

app.UseExceptionHandler("/OpsError/Error");
app.UseStaticFiles();
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.UseSession();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
app.MapControllerRoute(
    name: "admin",
    pattern: "{area:exists}/{controller=AdminHome}/{action=Index}/{id?}");

app.Run();
```

3. ? Create `appsettings.json` with all configuration keys
4. ? Configure LibMan (`libman.json`) for static assets

#### 4.2 Replace WCF Clients with Typed HttpClient (5 days)

**6 Typed Clients to Create:**

```csharp
public class DicoApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<DicoApiClient> _logger;

    public DicoApiClient(HttpClient httpClient, ILogger<DicoApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<List<BlocDTO>> GetBlocsAsync()
    {
        try
        {
            return await _httpClient.GetFromJsonAsync<List<BlocDTO>>("api/dico/blocs") 
                   ?? new List<BlocDTO>();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Error calling GetBlocs API");
            throw;
        }
    }

    // ... 30+ more methods
}
```

**Clients:**
1. `DicoApiClient`
2. `AdminApiClient`
3. `AcquisitionApiClient`
4. `DataApiClient`
5. `CosmetochemApiClient`
6. `MdmApiClient`

#### 4.3 Update MVC Controllers (5 days)

**14 MVC Controllers to Update:**

**Changes per controller:**
- ? Namespace: `System.Web.Mvc` ? `Microsoft.AspNetCore.Mvc`
- ? Replace `HttpContext.Current` ? inject `IHttpContextAccessor`
- ? Replace `Session["key"]` ? `HttpContext.Session.GetString("key")`
- ? Replace `ConfigurationManager` ? inject `IConfiguration`
- ? Replace WCF proxy calls ? inject typed `HttpClient` (make async)
- ? Update return types: `ActionResult` remains, but use `IActionResult` where appropriate

**Example:**

**Before:**
```csharp
public class HomeController : BaseController
{
    public ActionResult Search(SearchViewModel model)
    {
        var client = new ServiceDico.DicoServiceClient();
        var blocs = client.GetBlocs();
        return View(blocs);
    }
}
```

**After:**
```csharp
public class HomeController : BaseController
{
    private readonly DicoApiClient _dicoClient;
    private readonly ILogger<HomeController> _logger;

    public HomeController(
        DicoApiClient dicoClient,
        ILogger<HomeController> logger,
        IHttpContextAccessor httpContextAccessor,
        IConfiguration configuration)
        : base(httpContextAccessor, configuration)
    {
        _dicoClient = dicoClient;
        _logger = logger;
    }

    public async Task<IActionResult> Search(SearchViewModel model)
    {
        try
        {
            var blocs = await _dicoClient.GetBlocsAsync();
            return View(blocs);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Search");
            return View("Error");
        }
    }
}
```

#### 4.4 Update Web API 2 Controllers (3 days)

**11 API Controllers to Update:**
- ? Base class: `ApiController` ? `ControllerBase`
- ? Add: `[ApiController]` attribute
- ? Update: Return types to `ActionResult<T>`
- ? Update: Routing to `[Route("api/[controller]")]`

#### 4.5 Update 119 Razor Views (5 days)

**Changes per view:**
1. ? Update `@model` directives:
   - `@model OpenSafetyFrontend.ServiceAdmin.BlocDTO` ? `@model OpenSafetyContract.BlocDTO`
2. ? Update `using` directives (if present):
   - `@using System.Web.Mvc.Html` ? `@using Microsoft.AspNetCore.Mvc.Rendering`
3. ? Keep existing `@Html.*` helpers (compatible with Core)
4. ? Update `Ajax.BeginForm` views (add `Microsoft.jQuery.Unobtrusive.Ajax` package)

**12+ views with WCF proxy namespaces to update**

#### 4.6 Static Asset Management (2 days)

**Replace Bundle Config with LibMan:**

Create `libman.json`:
```json
{
  "version": "1.0",
  "defaultProvider": "cdnjs",
  "libraries": [
    {
      "library": "jquery@3.7.1",
      "destination": "wwwroot/lib/jquery/",
      "files": ["jquery.min.js", "jquery.min.map"]
    },
    {
      "library": "bootstrap@5.3.3",
      "destination": "wwwroot/lib/bootstrap/",
      "files": ["dist/css/bootstrap.min.css", "dist/js/bootstrap.bundle.min.js"]
    },
    {
      "library": "datatables@1.13.8",
      "destination": "wwwroot/lib/datatables/"
    }
  ]
}
```

#### 4.7 Replace jqGrid with DataTables.js (3 days)

**7 views using Trirand.jqGrid ? DataTables.js:**

**Before:**
```csharp
@Html.Trirand().JQGrid(Model.BlocsGrid, "grid")
    .Columns(cols => {
        cols.Add(c => c.Id).SetLabel("ID");
        cols.Add(c => c.Name).SetLabel("Name");
    })
```

**After:**
```html
<table id="blocsTable" class="table table-striped table-hover">
    <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
        </tr>
    </thead>
    <tbody></tbody>
</table>

<script>
$(document).ready(function() {
    $('#blocsTable').DataTable({
        ajax: '/api/blocs',
        columns: [
            { data: 'id' },
            { data: 'name' }
        ],
        pageLength: 25,
        responsive: true
    });
});
</script>
```

#### 4.8 Upgrade Bootstrap 3 ? 5 (2 days)

**37+ views with Bootstrap 3 classes:**

| Bootstrap 3 | Bootstrap 5 |
|-------------|-------------|
| `.panel-default` | `.card` |
| `.panel-heading` | `.card-header` |
| `.panel-body` | `.card-body` |
| `.glyphicon-*` | Use FontAwesome 6 or Bootstrap Icons |
| `.col-xs-*` | `.col-*` (XS breakpoint removed) |
| `.form-control-feedback` | `.form-control` + validation classes |

#### 4.9 Replace Static Helpers (2 days)

**RestHelper static class ? IHttpClientFactory:**
- ? Delete `RestHelper.cs` (527 lines)
- ? Replace all `RestHelper.Get()` / `RestHelper.Post()` calls with typed `HttpClient`

**OPSConfigHelper ? IConfiguration:**
- ? Delete static `OPSConfigHelper.GetWcfEndpoint()`
- ? Use `IConfiguration["ApiBaseUrl"]` instead

**Success Criteria:**
- All 14 MVC controllers functional
- All 119 views rendering correctly
- All 11 API controllers working
- Windows Authentication functional
- Session state working
- No WCF proxy dependencies remain

---

### Phase 5: Background Services & Utilities (Week 20 - 6 days)

#### 5.1 WsAsynchronousSilicoState ? Worker Service (3 days)

**Before (Windows Service):**
```csharp
public partial class WsAsynchronousSilicoState : ServiceBase
{
    private System.Timers.Timer timer;

    protected override void OnStart(string[] args)
    {
        timer = new System.Timers.Timer(30000);
        timer.Elapsed += (s, e) =>
        {
            var client = new ServiceSilicoClient();
            client.AnalyzeSilicoResult().Wait();
        };
        timer.Start();
    }
}
```

**After (.NET 8 Worker Service):**
```csharp
public class SilicoStateWorker : BackgroundService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ILogger<SilicoStateWorker> _logger;
    private readonly IConfiguration _configuration;

    public SilicoStateWorker(
        IHttpClientFactory httpClientFactory,
        ILogger<SilicoStateWorker> logger,
        IConfiguration configuration)
    {
        _httpClientFactory = httpClientFactory;
        _logger = logger;
        _configuration = configuration;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Silico State Worker starting");

        using var timer = new PeriodicTimer(TimeSpan.FromSeconds(30));

        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            try
            {
                await AnalyzeSilicoStateAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error analyzing silico state");
            }
        }
    }

    private async Task AnalyzeSilicoStateAsync(CancellationToken cancellationToken)
    {
        var httpClient = _httpClientFactory.CreateClient();
        var apiUrl = _configuration["ApiBaseUrl"];
        
        await httpClient.PostAsync(
            $"{apiUrl}/api/silico/analyze",
            null,
            cancellationToken);
        
        _logger.LogInformation("Silico state analysis triggered");
    }
}

// Program.cs:
var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddWindowsService(options =>
{
    options.ServiceName = "OpenSafety Silico State Worker";
});

builder.Services.AddHttpClient();
builder.Services.AddHostedService<SilicoStateWorker>();

var host = builder.Build();
await host.RunAsync();
```

**Changes:**
1. ? Replace `ServiceBase` ? `BackgroundService`
2. ? Replace `System.Timers.Timer` ? `PeriodicTimer`
3. ? Convert all blocking `.Result` / `.Wait()` ? `async`/`await`
4. ? Inject `IHttpClientFactory` for HTTP calls
5. ? Delete `ProjectInstaller.Designer.cs`, `.resx` files

#### 5.2 OpenSafetyStateChecker (1 day)
- ? Same pattern as 5.1
- ? **Decision Required:** Currently an empty stub (OnStart/OnStop have no logic)
  - Option A: Implement actual health-check logic
  - Option B: Retire the project

#### 5.3 JsonToSql Utility (1 day)
- ? Bump `netcoreapp3.1` ? `net8.0` in .csproj
- ? Update dependencies
- ? Test functionality

#### 5.4 ConsoleTest (1 day)
- ? Remove obsolete APIs: `System.Runtime.Remoting`, `JavaScriptSerializer`
- ? Replace `WebRequest` ? `HttpClient`
- ? **Decision Required:** 
  - Option A: Keep as internal dev tool
  - Option B: Retire (rarely used)

**Success Criteria:**
- Windows Services deploy and run as .NET 8 Worker Services
- Services restart correctly after crashes
- Logging works correctly

---

### Phase 6: Test Modernization (Week 21 - 9 days)

#### 6.1 Test Infrastructure Setup (2 days)
1. ? Convert test projects to xUnit
2. ? Add `Microsoft.AspNetCore.Mvc.Testing` (WebApplicationFactory<T>)
3. ? Add `Moq` 4.20+ for mocking
4. ? Add `FluentAssertions` 6.12+ for readable assertions
5. ? Add `AutoFixture` for test data generation

#### 6.2 API Integration Tests (3 days)

**Example Test Class:**
```csharp
public class DicoControllerIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public DicoControllerIntegrationTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetBlocs_ReturnsSuccessStatusCode()
    {
        // Act
        var response = await _client.GetAsync("/api/dico/blocs");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        
        var blocs = await response.Content.ReadFromJsonAsync<List<BlocDTO>>();
        blocs.Should().NotBeNull();
        blocs.Should().NotBeEmpty();
    }

    [Fact]
    public async Task GetBlocs_WithInvalidAuth_Returns401()
    {
        // Arrange
        _client.DefaultRequestHeaders.Clear(); // Remove auth

        // Act
        var response = await _client.GetAsync("/api/dico/blocs");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }
}
```

**Coverage:**
- ? Integration tests for all 8 API controllers (success + error paths)
- ? Test authentication/authorization
- ? Test error handling (4xx, 5xx responses)

#### 6.3 Unit Tests (3 days)

**Classes to Test:**

1. **Application Services:**
```csharp
public class DicoApplicationServiceTests
{
    [Fact]
    public async Task GetAllBlocs_ReturnsAllBlocs()
    {
        // Arrange
        var mockRepo = new Mock<IDicoRepository>();
        var fixture = new Fixture();
        var expectedBlocs = fixture.CreateMany<BlocEntity>(5).ToList();
        
        mockRepo.Setup(r => r.GetAllBlocsAsync())
            .ReturnsAsync(expectedBlocs);

        var service = new DicoApplicationService(
            mockRepo.Object,
            Mock.Of<ILogger<DicoApplicationService>>(),
            Mock.Of<IMapper>());

        // Act
        var result = await service.GetAllBlocsAsync();

        // Assert
        result.Should().HaveCount(5);
        mockRepo.Verify(r => r.GetAllBlocsAsync(), Times.Once);
    }
}
```

2. **Repositories:**
```csharp
public class EFDicoRepositoryTests
{
    [Fact]
    public async Task GetAllBlocs_ReturnsActiveBlocs()
    {
        // Arrange (use in-memory EF Core)
        var options = new DbContextOptionsBuilder<OpenSafetyDBContext>()
            .UseInMemoryDatabase(databaseName: "TestDb")
            .Options;

        await using var context = new OpenSafetyDBContext(options);
        await context.Blocs.AddAsync(new BlocEntity { Id = 1, Name = "Test" });
        await context.SaveChangesAsync();

        var repository = new EFDicoRepository(context);

        // Act
        var result = await repository.GetAllBlocsAsync();

        // Assert
        result.Should().HaveCount(1);
        result.First().Name.Should().Be("Test");
    }
}
```

3. **AutoMapper Profiles:**
```csharp
public class MappingProfileTests
{
    [Fact]
    public void AutoMapper_Configuration_IsValid()
    {
        // Arrange
        var config = new MapperConfiguration(cfg =>
        {
            cfg.AddProfile<DicoDomainProfile>();
            cfg.AddProfile<AcquisitionDomainProfile>();
        });

        // Act & Assert
        config.AssertConfigurationIsValid();
    }
}
```

#### 6.4 Code Coverage Configuration (1 day)

**Update Jenkins Pipeline:**
```groovy
stage('Test') {
    steps {
        bat '''
        dotnet test OpenSafety.sln ^
          -c Release ^
          --no-build ^
          --logger trx ^
          /p:CollectCoverage=true ^
          /p:CoverletOutputFormat=cobertura ^
          /p:CoverletOutput=./TestResults/Coverage/ ^
          /p:Threshold=60
        '''
    }
}

stage('Publish Coverage') {
    steps {
        cobertura coberturaReportFile: '**/TestResults/Coverage/coverage.cobertura.xml'
    }
}
```

**Success Criteria:**
- ? ?60% code coverage across solution
- ? All critical paths have integration tests
- ? Unit tests for all application services
- ? CI build fails if coverage drops below threshold

---

### Phase 7: CI/CD & Deployment (Week 22 - 4 days)

#### 7.1 Update Jenkins Pipelines (2 days)

**Jenkinsfile-Api (ASP.NET Core Web API):**
```groovy
pipeline {
    agent any
    
    environment {
        DOTNET_CLI_HOME = "/tmp/dotnet_cli"
    }
    
    stages {
        stage('Restore') {
            steps {
                bat 'dotnet restore OpenSafety.sln'
            }
        }
        
        stage('Build') {
            steps {
                bat 'dotnet build OpenSafety.sln -c Release --no-restore'
            }
        }
        
        stage('Test') {
            steps {
                bat 'dotnet test OpenSafety.sln -c Release --no-build --logger trx /p:CollectCoverage=true'
            }
            post {
                always {
                    mstest testResultsFile: '**/*.trx'
                }
            }
        }
        
        stage('Publish') {
            steps {
                bat '''
                dotnet publish OpenSafetyDistributedService\\OpenSafetyDistributedService.csproj ^
                  -c Release ^
                  -o ./publish/api ^
                  --no-build
                '''
            }
        }
        
        stage('Database Migration') {
            steps {
                bat '''
                dotnet ef database update ^
                  --project OPenSafetyInfrastructure ^
                  --startup-project OpenSafetyDistributedService ^
                  --connection "%CONNECTION_STRING%"
                '''
            }
        }
        
        stage('Deploy to IIS') {
            steps {
                // Use Web Deploy or xcopy
                bat '''
                net stop "OpenSafety API AppPool"
                xcopy /Y /E /I ./publish/api "C:\\inetpub\\wwwroot\\opensafety-api"
                net start "OpenSafety API AppPool"
                '''
            }
        }
    }
}
```

**Jenkinsfile-Frontend:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                bat 'dotnet build OpenSafetyFrontend\\OpenSafetyFrontend.csproj -c Release'
            }
        }
        
        stage('Publish') {
            steps {
                bat '''
                dotnet publish OpenSafetyFrontend\\OpenSafetyFrontend.csproj ^
                  -c Release ^
                  -o ./publish/frontend
                '''
            }
        }
        
        stage('Deploy to IIS') {
            steps {
                bat '''
                net stop "OpenSafety Frontend AppPool"
                xcopy /Y /E /I ./publish/frontend "C:\\inetpub\\wwwroot\\opensafety-frontend"
                net start "OpenSafety Frontend AppPool"
                '''
            }
        }
    }
}
```

#### 7.2 IIS Server Configuration (1 day)

**Prerequisites on ALL IIS servers (dev, pit, int, prod):**

1. ? Install **.NET 8 Windows Hosting Bundle**:
   - Download: https://dotnet.microsoft.com/download/dotnet/8.0
   - Reboot server after installation

2. ? Create Application Pools:
   ```
   Name: OpenSafety API AppPool
   .NET CLR Version: No Managed Code
   Managed Pipeline Mode: Integrated
   Identity: ApplicationPoolIdentity (or custom service account)
   
   Name: OpenSafety Frontend AppPool
   .NET CLR Version: No Managed Code
   Managed Pipeline Mode: Integrated
   Identity: ApplicationPoolIdentity (or custom service account)
   ```

3. ? Create IIS Applications:
   ```
   API:
   - Physical Path: C:\inetpub\wwwroot\opensafety-api
   - Application Pool: OpenSafety API AppPool
   - Binding: https://opensafety-api.company.com:443
   
   Frontend:
   - Physical Path: C:\inetpub\wwwroot\opensafety-frontend
   - Application Pool: OpenSafety Frontend AppPool
   - Binding: https://opensafety.company.com:443
   ```

4. ? Configure Windows Authentication:
   - Enable Windows Authentication in IIS
   - Disable Anonymous Authentication (if required)
   - Configure Negotiate provider (Kerberos first, NTLM fallback)

**web.config for ASP.NET Core (auto-generated by publish):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <location path="." inheritInChildApplications="false">
    <system.webServer>
      <handlers>
        <add name="aspNetCore" path="*" verb="*" modules="AspNetCoreModuleV2" resourceType="Unspecified" />
      </handlers>
      <aspNetCore processPath="dotnet"
                  arguments=".\OpenSafetyDistributedService.dll"
                  stdoutLogEnabled="true"
                  stdoutLogFile=".\logs\stdout"
                  hostingModel="inprocess" />
    </system.webServer>
  </location>
</configuration>
```

#### 7.3 Deployment Strategy - Strangler Fig Pattern (1 day)

**Week 1-2: Parallel Deployment**
1. ? Deploy new .NET 8 API to `/api-v2` endpoint
2. ? Keep existing WCF services running at `/services/`
3. ? Frontend uses feature flag to route to WCF or new API:
```csharp
public class ApiClientFactory
{
    public IApiClient CreateClient(string serviceName)
    {
        if (_configuration["UseNewApi:Dico"] == "true")
            return new DicoApiClient(_httpClientFactory);
        else
            return new DicoWcfClient(); // Legacy
    }
}
```

**Week 3-4: Gradual Migration**
1. ? Enable new API for internal users (feature flag)
2. ? Monitor both systems (metrics, logs, errors)
3. ? Compare response times and error rates
4. ? Gradually increase % of traffic to new API

**Week 5-6: External Consumer Migration**
1. ? Audit all external systems calling WCF endpoints
2. ? Contact each team with migration guide
3. ? Provide new API documentation (Swagger)
4. ? Set WCF deprecation date (e.g., +3 months)

**Week 7+: Decommission WCF**
1. ? Set feature flags to 100% new API
2. ? Add warning headers to WCF responses: `X-Deprecated: true`
3. ? Monitor for any remaining WCF traffic
4. ? Turn off WCF services after deprecation period

**Rollback Plan:**
- ? Keep WCF services running for 3 months
- ? Feature flags allow instant rollback
- ? Database schema supports both systems (no breaking changes)
- ? Documented rollback procedure for each environment

**Success Criteria:**
- ? CI/CD pipeline successfully builds and deploys .NET 8 apps
- ? IIS hosting configured correctly (No Managed Code)
- ? Strangler Fig pattern implemented with feature flags
- ? Monitoring and alerting configured
- ? Rollback procedure tested

---

## 4. Risk Management

### 4.1 Critical Risks (RED)

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| **R1** | **External WCF consumers break during cutover** | ?? HIGH | ?? CRITICAL | **Strangler Fig Pattern**: Deploy new API alongside WCF; maintain both for 3 months; audit all external consumers; provide migration guide; set explicit deprecation timeline |
| **R2** | **Elasticsearch cluster version mismatch** (cluster on 6.x, client requires 8.x) | ?? MEDIUM | ?? HIGH | **Pre-Migration**: Upgrade ES cluster to 8.x before .NET upgrade; OR use NEST 7.x as intermediate step; test all queries on new cluster before deployment |
| **R3** | **EF Core migration generates incorrect schema** | ?? MEDIUM | ?? HIGH | **Validation**: Run `dotnet ef dbcontext scaffold` on production DB to reverse-engineer current schema; compare with EF6 model; test migrations on production copy; use `dotnet ef migrations script` to review SQL before execution |
| **R4** | **Production data loss during EF Core migration** | ?? LOW | ?? CRITICAL | **Safety**: Full database backup before migration; test migrations on production copy; use transaction scopes; implement rollback scripts |

### 4.2 High Risks (ORANGE)

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| **R5** | **Trirand.jqGrid replacement breaks grid functionality** (no drop-in replacement) | ?? HIGH | ?? MEDIUM | **Planning**: Define feature parity requirements upfront (pagination, sorting, filtering, export); allocate 3 dedicated days for 7 grid views; test with real data; get user acceptance before deployment |
| **R6** | **AutoMapper 5?13 upgrade breaks unmapped properties** | ?? MEDIUM | ?? MEDIUM | **Validation**: Run `cfg.AssertConfigurationIsValid()` in startup integration tests; fix all mapping errors before deployment; add unit tests for all mapping profiles |
| **R7** | **Session state incompatibility** (ASP.NET ? ASP.NET Core) | ?? MEDIUM | ?? MEDIUM | **Solution**: Use distributed cache (Redis/SQL Server) for session state; test session behavior during app pool recycling; convert session objects to JSON strings if needed |
| **R8** | **Windows Auth (Kerberos/NTLM) configuration issues** | ?? MEDIUM | ?? MEDIUM | **Testing**: Validate Negotiate auth in all environments; verify SPNs configured for service accounts; test with different browsers; check IIS authentication settings |
| **R9** | **Large controllers (1,500+ lines) introduce bugs during refactoring** | ?? MEDIUM | ?? MEDIUM | **Process**: Write characterization tests before refactoring; decompose incrementally; thorough code reviews; compare outputs with legacy system |

### 4.3 Medium Risks (YELLOW)

| # | Risk | Mitigation |
|---|------|------------|
| **R10** | **Bootstrap 3?5 CSS breaking changes affect UI** | Allocate 2 dedicated days for CSS updates; test all 119 views in browser matrix; maintain visual regression test suite |
| **R11** | **Async/await introduction causes deadlocks** | Avoid `.Result`/`.Wait()` entirely; use `ConfigureAwait(false)` in library code; load test all async endpoints |
| **R12** | **Third-party package breaking changes** (ClosedXML, DocumentFormat.OpenXml) | Review changelog for each package upgrade; test Excel export functionality; allocate buffer time for fixes |
| **R13** | **Log output differences** (log4net ? Serilog) | Configure Serilog sinks to match existing log format; test structured logging; verify log aggregation tools still work |
| **R14** | **Configuration secrets exposed** | Use Azure Key Vault for all secrets; never commit `appsettings.Production.json`; rotate all credentials in Phase 0; implement secret scanning in CI/CD |

### 4.4 Risk Response Plan

**If WCF consumers break (R1):**
1. Immediately revert feature flag to route traffic back to WCF
2. Identify broken endpoints via monitoring
3. Contact affected external teams
4. Fix issues in new API
5. Re-test before re-enabling

**If EF Core migration fails (R3, R4):**
1. Restore database from backup
2. Review migration SQL scripts for errors
3. Test on production copy again
4. Consider manual schema migration if necessary
5. Do not proceed to next phase until resolved

**If critical dependency upgrade fails (R6, R12):**
1. Roll back to previous package version
2. Investigate breaking changes in package changelog
3. Implement adapter/wrapper layer if necessary
4. Consider alternative package if issues persist

---

## 5. Success Metrics & KPIs

### 5.1 Technical Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| **Framework Version** | .NET Framework 4.7.1 | .NET 8.0 | All projects targeting `net8.0` |
| **Incompatible API Usage** | 225 files (39%) | 0 files | Static code analysis |
| **Code Coverage** | ~0% | ?60% | Coverlet + Cobertura |
| **Build Time** | ~8 minutes (MSBuild) | ?5 minutes | `dotnet build` |
| **Dead Code (LOC)** | ~5,000 lines | 0 lines | Removed in Phase 0 |
| **Nullable Reference Types** | Disabled | Enabled | `<Nullable>enable</Nullable>` |

### 5.2 Performance Metrics

| Metric | Baseline (WCF/.NET FW) | Target (.NET 8) | Measurement |
|--------|------------------------|-----------------|-------------|
| **API Response Time (p95)** | TBD (measure before migration) | ? baseline | Application Insights |
| **Memory Usage** | TBD | ? 80% of baseline | Performance Monitor |
| **Throughput (req/sec)** | TBD | ? 120% of baseline | Load testing |
| **Cold Start Time** | ~15 seconds | ?10 seconds | IIS logs |
| **Database Query Time** | TBD | ? baseline | EF Core logging |

### 5.3 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Critical Bugs (Production)** | 0 in first 30 days | Incident tracking |
| **Rollbacks Required** | 0 | Deployment logs |
| **External Consumer Breakage** | 0 | Support tickets |
| **Test Pass Rate** | 100% | CI/CD dashboard |
| **Security Vulnerabilities** | 0 critical/high | Dependency scanning |

### 5.4 Operational Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Deployment Frequency** | No change (maintain current cadence) | Jenkins metrics |
| **Mean Time to Recovery (MTTR)** | ?2 hours | Incident tracking |
| **Uptime / Availability** | ?99.9% | Monitoring |
| **Developer Onboarding Time** | ?5 days (new .NET 8 stack) | Team survey |

---

## 6. Current Status & Next Steps

### 6.1 Current Status: NOT STARTED

**Last Update:** 2024  
**Overall Progress:** 0%

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 0: Preparation | ? Not Started | 0% |
| Phase 1: Foundation | ? Not Started | 0% |
| Phase 2: Infrastructure | ? Not Started | 0% |
| Phase 3: API Migration | ? Not Started | 0% |
| Phase 4: Frontend | ? Not Started | 0% |
| Phase 5: Services | ? Not Started | 0% |
| Phase 6: Tests | ? Not Started | 0% |
| Phase 7: Deployment | ? Not Started | 0% |

### 6.2 Immediate Next Steps (Week 1)

**Before Starting Migration:**

1. ? **Executive Approval**
   - Present this report to stakeholders
   - Secure budget for 22-week timeline (1-2 developers)
   - Get approval for Strangler Fig deployment strategy
   - Approve 3-month WCF deprecation period

2. ? **Pre-Migration Audit**
   - Document all external systems calling WCF services
   - Inventory all production environment configurations
   - Backup all databases
   - Document current performance baselines

3. ? **Team Preparation**
   - Install .NET 8 SDK on all developer machines
   - Set up .NET 8 development environment (VS 2022 17.8+)
   - Training: ASP.NET Core, EF Core, async/await patterns
   - Assign roles (if 2 developers): Dev 1 = Backend, Dev 2 = Frontend

4. ? **Infrastructure Preparation**
   - Upgrade Elasticsearch cluster from 6.x ? 8.x (if in use)
   - Install .NET 8 Hosting Bundle on DEV IIS server
   - Set up test environment for parallel WCF/API deployment
   - Configure monitoring/alerting for new .NET 8 apps

5. ? **Start Phase 0** (Day 1 of migration)
   - Create branch: `git checkout -b feature/dotnet8-migration`
   - Install tools: `dotnet tool install -g upgrade-assistant`, `dotnet-ef`
   - Run analysis: `upgrade-assistant analyze OpenSafety.sln`
   - Begin cleanup: rotate credentials, remove dead code

### 6.3 Decision Points Requiring Input

| # | Decision | Options | Recommendation | Owner |
|---|----------|---------|----------------|-------|
| **D1** | OpenSafetyStateChecker project (empty stub) | A) Implement logic<br>B) Retire project | **B) Retire** - No logic in 5+ years | Tech Lead |
| **D2** | ConsoleTest project (dev tool) | A) Keep & update<br>B) Retire | **B) Retire** - Rarely used | Tech Lead |
| **D3** | Bootstrap version | A) Stay on 3.x<br>B) Upgrade to 5.x | **B) Upgrade** - 3.x EOL, security | Product Owner |
| **D4** | jqGrid replacement | A) DataTables.js<br>B) AG Grid CE<br>C) Custom | **A) DataTables.js** - Free, mature | Tech Lead |
| **D5** | Logging sink | A) Serilog + Seq<br>B) Serilog + ELK<br>C) Application Insights | **C) Application Insights** - Azure native | DevOps |
| **D6** | Session storage | A) In-memory<br>B) Redis<br>C) SQL Server | **B) Redis** - Scalable, fast | Tech Lead |
| **D7** | Deployment automation | A) Jenkins + Web Deploy<br>B) Azure DevOps<br>C) GitHub Actions | **A) Jenkins** - Existing pipeline | DevOps |

### 6.4 Resource Requirements

**Team:**
- **Option A** (22 weeks): 1 Senior .NET Developer
- **Option B** (12-14 weeks): 2 Senior .NET Developers
- **Shared**: 1 DevOps Engineer (10% allocation for CI/CD updates)
- **Shared**: 1 QA Engineer (20% allocation for testing Phase 6)

**Recommended:** **Option B** (2 developers, 12-14 weeks)

**Infrastructure:**
- .NET 8 SDK (free)
- Visual Studio 2022 Professional (2 licenses) or VS Code (free)
- Azure Key Vault (existing subscription)
- Redis Cache for session state (optional, ~$50/month for dev)
- Elasticsearch 8.x cluster upgrade (coordinate with Ops)

**Training:**
- ASP.NET Core fundamentals (40 hours total per developer)
- EF Core migration patterns (8 hours)
- Async/await best practices (4 hours)

---

## 7. Appendix

### 7.1 Key Dependencies

**NuGet Packages - Current ? Target:**

| Package | Current | Target | Breaking Changes |
|---------|---------|--------|------------------|
| Entity Framework | 6.1.3 | EF Core 8.0.11 | Complete API rewrite |
| NEST / Elasticsearch.Net | 6.1.0 | Elastic.Clients.Elasticsearch 8.15.0 | Query DSL changes |
| Unity | 4.0.1 / 5.11.6 | Remove (built-in DI) | Complete replacement |
| AutoMapper | 5.1.1 | 13.0.1 | Static API removed |
| log4net | 2.0.8 | Remove (Microsoft.Extensions.Logging) | Different API |
| Newtonsoft.Json | 4.5.11-12.0.3 | 13.0.3 | Minor (backward-compatible) |
| ClosedXML | 0.95.2 | 0.102.2 | Some API changes |
| Bootstrap | 3.3.7 | 5.3.3 | CSS breaking changes |
| jQuery | 1.10.2 / 3.3.1 | 3.7.1 | Align versions |
| Trirand.jqGrid | 4.6.0 | Remove (DataTables.js) | Complete replacement |

**New Packages to Add:**

| Package | Version | Purpose |
|---------|---------|---------|
| `Microsoft.EntityFrameworkCore` | 8.0.11 | ORM |
| `Microsoft.EntityFrameworkCore.SqlServer` | 8.0.11 | EF Core SQL Server provider |
| `Microsoft.EntityFrameworkCore.Tools` | 8.0.11 | EF Core CLI tools |
| `Elastic.Clients.Elasticsearch` | 8.15.0 | Elasticsearch client |
| `Microsoft.Extensions.Logging` | 8.0.1 | Logging abstractions |
| `Serilog.AspNetCore` | 8.0.1 | Logging implementation |
| `Microsoft.AspNetCore.Authentication.Negotiate` | 8.0.11 | Windows Auth |
| `Microsoft.jQuery.Unobtrusive.Ajax` (Core) | 4.0.0 | Ajax helpers |
| `X.PagedList.Mvc.Core` | 9.1.2 | Pagination |
| `MailKit` | 4.7.1 | SMTP client |
| `Moq` | 4.20.72 | Mocking framework |
| `FluentAssertions` | 6.12.1 | Test assertions |
| `xunit` | 2.9.2 | Test framework |
| `Microsoft.AspNetCore.Mvc.Testing` | 8.0.11 | Integration testing |

### 7.2 Reference Documentation

**Official Microsoft Guides:**
- .NET 8 Migration: https://learn.microsoft.com/en-us/aspnet/core/migration/
- EF6 ? EF Core: https://learn.microsoft.com/en-us/ef/efcore-and-ef6/porting/
- WCF ? ASP.NET Core: https://learn.microsoft.com/en-us/aspnet/core/grpc/wcf
- Upgrade Assistant: https://dotnet.microsoft.com/platform/upgrade-assistant

**Third-Party Resources:**
- AutoMapper 13 Migration: https://docs.automapper.org/en/stable/
- Elasticsearch .NET Client 8: https://www.elastic.co/guide/en/elasticsearch/client/net-api/current/index.html
- Serilog ASP.NET Core: https://github.com/serilog/serilog-aspnetcore
- DataTables.js: https://datatables.net/

### 7.3 Contact Information

**Project Team:**
- **Technical Lead:** [Name] - [Email]
- **Product Owner:** [Name] - [Email]
- **DevOps Lead:** [Name] - [Email]
- **QA Lead:** [Name] - [Email]

**Escalation Path:**
- **Technical Issues:** Tech Lead ? Engineering Manager
- **Schedule/Budget:** Product Owner ? Director
- **Infrastructure:** DevOps Lead ? Infrastructure Manager

### 7.4 Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024 | GitHub Copilot | Initial upgrade report created from comprehensive analysis |

---

## 8. Executive Summary & Recommendation

### 8.1 Summary

The OpenSafety solution upgrade from .NET Framework 4.7.1 to .NET 8.0 represents a **significant but achievable modernization effort**. The solution consists of 18 projects (~78,600 LOC) with 39% of files requiring updates due to API incompatibilities.

**Key Challenges:**
- Complete replacement of WCF services (8 services ? ASP.NET Core Web API)
- Entity Framework 6 ? EF Core 8 migration (65 files, 14 migrations)
- Elasticsearch client upgrade (deprecated NEST 6.x ? modern client 8.x)
- Frontend modernization (119 Razor views, 25 controllers)

**Key Opportunities:**
- Remove ~5,000 lines of dead code
- Improve performance (expected 20%+ throughput increase)
- Reduce hosting costs (more efficient runtime)
- Enable modern development practices (nullable types, async/await)
- Establish comprehensive test suite (currently ~0% coverage)

### 8.2 Recommended Approach

**Strategy:** Phased migration over **12-14 weeks** with **2 developers** using **Strangler Fig pattern**

**Why this approach:**
1. **Risk Mitigation:** Parallel deployment (WCF + new API) allows safe rollback
2. **Predictable Timeline:** Bottom-up migration with clear phase gates
3. **Quality Focus:** Dedicated test modernization phase (Phase 6)
4. **Minimal Disruption:** External consumers have 3-month migration window

**Not Recommended:**
- ? Big bang migration (too risky)
- ? Partial migration (creates technical debt)
- ? Rewrite from scratch (too expensive, loses domain knowledge)

### 8.3 Go/No-Go Recommendation

**? RECOMMENDED: PROCEED WITH MIGRATION**

**Justification:**
- .NET Framework 4.7.1 reaches end of support (no security updates)
- .NET 8 offers significant performance and cost benefits
- Manageable risk with Strangler Fig pattern
- Reasonable timeline (12-14 weeks with 2 developers)
- Solution architecture is relatively clean (good layering)

**Prerequisites Before Starting:**
1. ? Executive approval for 12-14 week timeline
2. ? Assign 2 senior .NET developers (full-time)
3. ? Upgrade Elasticsearch cluster to 8.x
4. ? Audit all external WCF consumers
5. ? Secure budget for Redis, monitoring tools

**Stop Conditions (Re-evaluate if encountered):**
- ? Critical external WCF consumers cannot migrate within 3 months
- ? Elasticsearch upgrade fails or causes data issues
- ? EF Core migration generates irreconcilable schema differences
- ? Timeline extends beyond 20 weeks (indicating unforeseen blockers)

### 8.4 Expected ROI

**Benefits (Year 1):**
- **Performance:** 20-30% faster response times (.NET 8 runtime optimizations)
- **Hosting Costs:** 15-20% reduction (more efficient memory usage)
- **Developer Productivity:** 25% faster build times (SDK-style projects)
- **Security:** Modern framework with active security support
- **Maintainability:** Removal of 5,000 LOC dead code, 60% test coverage

**Investment:**
- **Development Effort:** 92 developer-days (~$92K at $1K/day blended rate)
- **Infrastructure:** Negligible (mostly free tools, Azure Key Vault already exists)
- **Risk Mitigation:** Strangler Fig pattern adds ~10% timeline but eliminates big bang risk

**Payback Period:** Estimated 8-12 months (cost savings + productivity gains)

---

**READY TO PROCEED: Awaiting executive approval to begin Phase 0**

---

*End of Upgrade Report*
