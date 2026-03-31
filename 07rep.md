# OpenSafety .NET 8 Migration Report

## Executive Summary

**Project:** OpenSafety - Enterprise Chemical Safety Management System  
**Current State:** .NET Framework 4.7.1 (18 projects, 578 source files)  
**Target State:** .NET 8 LTS  
**Migration Approach:** Strangler Fig pattern with parallel deployment  
**Estimated Effort:** 92 developer-days (single developer) or 55 developer-days (two developers in parallel)  
**Timeline:** 15-22 weeks

---

## 1. Current Architecture Overview

### 1.1 Solution Structure

OpenSafety is a multi-tier enterprise application built on classic n-tier architecture with Domain-Driven Design principles:
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

1.2 Project Inventory
#	Project	Type	Framework	Status	Action
1	OpenSafetyCrossCutting	Library	.NET FW 4.7.1	✅ Active	Migrate
2	OpenSafetyDomainModel	Library	.NET FW 4.7.1	✅ Active	Migrate
3	OpenSafetyContract	Library	.NET FW 4.7.1	✅ Active	Migrate
4	OPenSafetyInfrastructure	Library	.NET FW 4.7.1	✅ Active	Migrate
5	OpenSafetyApplication	Library	.NET FW 4.7.1	✅ Active	Migrate
6	OpenSafetyDependancyResolver	Library	.NET FW 4.7.1	✅ Active	Dissolve
7	OpenSafetyDistributedService	Web App	.NET FW 4.7.1	✅ Active	Migrate
8	OpenSafetyFrontend	Web App	.NET FW 4.7.1	✅ Active	Migrate
9	WsAsynchronousSilicoState	Win Service	.NET FW 4.7.1	✅ Active	Migrate
10	OpenSafetyStateChecker	Win Service	.NET FW 4.7.1	⚠️ Empty	Evaluate
11	JsonToSql	Console	.NET Core 3.1	✅ Active	Upgrade
12	ConsoleTest	Console	.NET FW 4.7.1	⚠️ Dev Tool	Retire
13	OpenSafetyDistributedService.Tests	Test	.NET FW 4.7.1	⚠️ Minimal	Migrate
14	OpenSafetyFrontend.Tests	Test	.NET FW 4.7.1	⚠️ Minimal	Migrate
15	WebFrontendTest	Stub	.NET FW 4.7.1	❌ Empty	Remove
16	OpenSafetyFrontedApplication	Stub	.NET FW 4.5.2	❌ Empty	Remove
17	Fronted.Tests	Stub	.NET FW 4.5.2	❌ Empty	Remove
18	WebApiOpenSafety	Stub	.NET FW 4.7.1	❌ Empty	Remove
Summary:
•	12 projects require full migration to .NET 8
•	1 project dissolves into host projects (DependancyResolver)
•	4 projects to be removed (stubs/scaffolds)
•	1 project requires minor upgrade (.NET Core 3.1 → .NET 8)
---
2. Critical Issues Requiring Immediate Action
2.1 🔴 CRITICAL: Exposed Credentials in Source Control
Severity: Critical
Location: OpenSafetyDistributedService/Web.config
Issue: Plaintext database password and application password committed to Git:
<connectionStrings>
    <add name="OpenSafetyDBContext" 
         connectionString="...Password=DBadmin@123456789..." />
</connectionStrings>
<appSettings>
    <add key="Password" value="OPSty!4Pit#18" />
</appSettings>

Required Actions:
1.	⚠️ Immediate: Rotate both credentials (coordinate with DBA)
2.	Rewrite Git history to remove credentials from all commits (BFG Repo-Cleaner)
3.	Add Web.config and App.config to .gitignore
4.	Store all secrets in Azure Key Vault
5.	Update deployment pipelines to inject secrets at runtime
Timeline: Must be completed before any code migration work begins
---
2.2 🔴 HIGH: WCF Service Layer (Not Compatible with .NET 8)
Severity: High
Impact: 8 WCF services, 225 source files (39% of codebase)
The entire service layer is built on Windows Communication Foundation (WCF), which does not run on .NET Core/.NET 8:
WCF Service	Endpoints	Consumers
OpenSafetyDicoWCFService	15 operations	Frontend (6 service references)
OpenSafetyAdminWCFService	28 operations	Frontend, External apps
OpenSafetyAcquisitionWCFService	12 operations	Frontend
OpenSafetyDataWCFService	18 operations	Frontend, Reporting
OpenSafetyCosmetochemWCFService	8 operations	Frontend, Background service
OpenSafetyMdmWCFService	6 operations	Frontend
OpenSafetyMpnetWCFService	7 operations	Frontend
OpenSafetySynonymsWCFService	4 operations	Frontend
Migration Strategy:
•	Replace all 8 WCF services with ASP.NET Core 8 Web API controllers
•	Use Strangler Fig pattern: Deploy new REST API alongside existing WCF during transition
•	Replace WCF client proxies in frontend with typed HttpClient via IHttpClientFactory
•	Maintain parallel WCF and REST endpoints during gradual consumer migration
---
2.3 🔴 HIGH: Entity Framework 6 → EF Core 8
Severity: High
Complexity: Very High
Current State:
•	Entity Framework 6.1.3 (not compatible with .NET 8)
•	31 EntityTypeConfiguration<T> classes
•	14 EF6 migrations (not compatible with EF Core)
•	DbContext with connection string-based constructor
Required Changes:
Component	EF6	EF Core 8
Base class	EntityTypeConfiguration<T>	IEntityTypeConfiguration<T>
Model builder	DbModelBuilder	ModelBuilder
Configuration	modelBuilder.Configurations.Add(...)	modelBuilder.ApplyConfiguration(...)
Constructor	DbContext(string connString)	DbContext(DbContextOptions<T>)
Lazy loading	Configuration.ProxyCreationEnabled	UseLazyLoadingProxies()
Migrations	14 DbMigration classes	Must regenerate as single baseline
Migration Plan:
1.	Generate new EF Core baseline migration from production schema
2.	Validate against current database using schema comparison
3.	Delete all 29 EF6 migration files after verification
4.	Update all 31 entity type configurations to EF Core API
---
2.4 🟡 MEDIUM: HttpClient Socket Exhaustion Risk
Severity: Medium
Files Affected: 13 files
Issue: Direct instantiation of HttpClient inside using blocks:
// Anti-pattern in RestHelper.cs and application services
using (var handler = new HttpClientHandler())
using (var client = new HttpClient(handler))
{
    var result = client.GetAsync(url).Result;  // Also blocking .Result
}
Problems:
•	Socket exhaustion under load (DNS changes not respected)
•	Blocking .Result calls risk deadlocks
•	No connection pooling
Solution: Replace with IHttpClientFactory pattern:
// Program.cs registration
builder.Services.AddHttpClient<CosmetochemApiClient>();

// Injection in services
public class CosmetochemService(HttpClient client) 
{
    public async Task<Result> GetDataAsync() 
        => await client.GetFromJsonAsync<Result>(...);
}
3. Architecture Violations to Fix
3.1 Layer Violation: Infrastructure → Frontend
Issue: OPenSafetyInfrastructure project has a direct reference to OpenSafetyFrontend
Location: GenericRepository.cs line 87
using OpenSafetyFrontend.ServiceAdmin;  // ❌ Infrastructure referencing UI

Root Cause: BlocColonneDTO is defined in the frontend WCF proxy namespace instead of the contract layer.
Fix Required:
1.	Move BlocColonneDTO to OpenSafetyContract project
2.	Remove <ProjectReference> to Frontend from Infrastructure .csproj
3.	Update all using directives
Impact: Blocks proper build order; must be fixed in Phase 0 before any migration work
---
3.2 Duplicate Configuration Files
Issue: 8 copies of UnityConfig.cs across projects (7 are empty stubs)
Project	Lines	Registrations
OpenSafetyDependancyResolver	157	✅ Real (production)
OpenSafetyApplication	12	❌ Empty stub
OpenSafetyContract	12	❌ Empty stub
OpenSafetyCrossCutting	12	❌ Empty stub
OpenSafetyDistributedService	12	❌ Empty stub
OpenSafetyDomainModel	12	❌ Empty stub
OPenSafetyInfrastructure	12	❌ Empty stub
OpenSafetyDependancyResolver/App_Start	12	❌ Empty stub
Solution: Delete all 7 stubs; migrate real registrations to Program.cs in Phase 3
---
4. Technology Stack Migration Map
4.1 Core Framework Changes
Component	Current	Target	Breaking Changes
Runtime	.NET Framework 4.7.1	.NET 8 LTS	Complete platform migration
Web Framework	ASP.NET MVC 5.2.3	ASP.NET Core MVC 8	System.Web removed
Web API	ASP.NET Web API 2	ASP.NET Core Web API 8	System.Web.Http removed
WCF	System.ServiceModel	None (replace with REST API)	Complete rewrite required
ORM	Entity Framework 6.1.3	EF Core 8.0.8	API changes, migrations incompatible
DI Container	Unity 5.2.1/5.11.6	Microsoft.Extensions.DI (built-in)	Complete pattern change
Logging	log4net 2.0.8	ILogger<T> + Serilog	Static API → injection
Configuration	ConfigurationManager	IConfiguration/IOptions<T>	Static API → injection
Session	HttpContext.Current.Session	ISession	Context access change
Caching	System.Runtime.Caching	IMemoryCache	API change
4.2 Package Migrations
Package	Current	Target	Complexity
AutoMapper	5.1.1	13.0.1	🟡 Medium - Static API removed
NEST / Elasticsearch.Net	6.1.0	Elastic.Clients.Elasticsearch 8.14.6	🔴 High - Complete rewrite
Newtonsoft.Json	6.0.4–12.0.3 (mixed)	13.0.3	🟢 Low - Align versions
ClosedXML	0.95.2	0.102.2	🟢 Low - Compatible upgrade
DocumentFormat.OpenXml	2.9.1–2.10.1	3.1.0	🟡 Medium - Namespace changes
Bootstrap	3.3.7	5.3.3	🔴 High - CSS class breaking changes
jQuery	1.10.2 / 3.3.1 (mixed)	3.7.1	🟡 Medium - Align versions
PagedList.Mvc	4.5.0	X.PagedList.Mvc.Core 9.1.2	🟢 Low - Drop-in replacement
Trirand.jqGrid	4.6.0	None (migrate to DataTables.js)	🔴 High - No .NET 8 port
Swashbuckle	6.0.0-rc1	Swashbuckle.AspNetCore 6.8.1	🟡 Medium - Different package
4.3 Packages to Remove
Package	Reason
Microsoft.AspNet.Mvc	Replaced by ASP.NET Core (built-in)
Microsoft.AspNet.WebApi.*	Replaced by ASP.NET Core (built-in)
Microsoft.CodeDom.Providers.DotNetCompilerPlatform	Roslyn built-in on .NET 8
Microsoft.Net.Compilers	Roslyn built-in on .NET 8
Owin / WebActivatorEx	Not needed in ASP.NET Core
WebGrease	System.Web.Optimization only
Unity / Unity.Mvc5 / CommonServiceLocator	Replaced by built-in DI
Modernizr	Obsolete for modern browsers
---
5. Migration Strategy
5.1 Approach: Strangler Fig Pattern
We will not perform a "big bang" migration. Instead:
1.	New .NET 8 API runs alongside WCF during transition
•	New endpoint: https://server/opensafety-api/api/dico/...
•	Old endpoint: https://server/OpenSafetyWS/OpenSafetyDicoWCFService.svc/...
2.	Gradual consumer migration
•	Frontend migrates to new API first
•	External consumers migrate on their own timeline
•	WCF remains online until all consumers confirm migration
3.	Database migration at deployment
•	EF Core migrations run automatically at app startup
•	No manual SQL script execution required
4.	Rollback capability
•	WCF endpoints remain available for 2 weeks post-deployment
•	Database backup taken before migration
•	IIS configuration allows instant switch-back
5.2 Build Order (Bottom-Up)
Projects must be migrated in strict dependency order:
Phase 1: Foundation (no dependencies)
  ┌─→ OpenSafetyCrossCutting

Phase 2: Domain Layer
  └─→ OpenSafetyDomainModel → OpenSafetyContract

Phase 3: Infrastructure + Application
  └─→ OPenSafetyInfrastructure → OpenSafetyApplication

Phase 4: Service Layer
  └─→ OpenSafetyDistributedService (WCF → Web API)

Phase 5: Frontend
  └─→ OpenSafetyFrontend (MVC 5 → ASP.NET Core MVC)

Phase 6: Background Services
  └─→ WsAsynchronousSilicoState (ServiceBase → BackgroundService)

Phase 7: Tests
  └─→ Test projects (MSTest → xUnit)

  6. Detailed Migration Plan
Phase 0: Preparation (Week 1 - 5 days)
Critical blockers before code migration can begin
Task	Duration	Priority
🔴 Rotate exposed credentials	0.5 day	CRITICAL
Fix Infrastructure→Frontend layer violation	1 day	CRITICAL
Install .NET 8 SDK + tools	0.5 day	Required
Remove 4 stub projects	1 day	Cleanup
Delete duplicate/dead files	1 day	Cleanup
Run upgrade-assistant analysis	1 day	Planning
Deliverables:
•	[ ] Credentials rotated; secrets in Azure Key Vault
•	[ ] Layer violation fixed; solution builds cleanly
•	[ ] Stub projects removed from solution
•	[ ] Upgrade analysis report generated
•	[ ] Git tag: phase0-complete
---
Phase 1: Foundation Libraries (Weeks 2-3 - 6 days)
Migrate CrossCutting, DomainModel, Contract to .NET 8
Sprint 1.1: OpenSafetyCrossCutting (3 days)
Changes Required:
File	Action
Class/GenerateCsvFile.cs	Remove HttpContext.Current.Response; inject IHttpContextAccessor
Class/OpsEmailSender.cs	Replace SmtpClient with MailKit
Class/CacheManager.cs	Replace MemoryCache with IMemoryCache
All files	Replace log4net with ILogger<T>
App_Start/UnityConfig.cs	Delete
SimpleJson.cs	Delete (2,127 lines, redundant)
New .csproj:
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="ClosedXML" Version="0.102.2" />
    <PackageReference Include="DocumentFormat.OpenXml" Version="3.1.0" />
    <PackageReference Include="MailKit" Version="4.7.1" />
    <PackageReference Include="Microsoft.Extensions.Caching.Memory" Version="8.0.1" />
    <PackageReference Include="Microsoft.Extensions.Logging.Abstractions" Version="8.0.2" />
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  </ItemGroup>
</Project>
Sprint 1.2: OpenSafetyDomainModel (1 day)
Changes Required:
•	Delete App_Start/UnityConfig.cs
•	Delete IRepository.cs / DicoDomainSpecification.cs (unused)
•	Enable <Nullable>enable</Nullable>
•	Remove all Unity, MVC references
Sprint 1.3: OpenSafetyContract (2 days)
Changes Required:
•	Strip all WCF attributes from 9 service interfaces:
•	Remove [ServiceContract]
•	Remove [OperationContract]
•	Remove [WebGet], [WebInvoke]
•	Remove all using System.ServiceModel.*
•	Delete App_Start/UnityConfig.cs
•	All 93 DTOs require no changes (plain C# POCOs)
Deliverables:
•	[ ] All 3 projects build on .NET 8 with 0 errors
•	[ ] All packages.config deleted
•	[ ] No System.ServiceModel references remain
•	[ ] Git tag: phase1-complete
---
Phase 2: Infrastructure & Application (Weeks 4-8 - 17 days)
Most technically complex phase: EF Core migration + Elasticsearch rewrite
Sprint 2.1: OPenSafetyInfrastructure - EF Core 8 (5 days)
Entity Framework Migration:
Component	Change
OpenSafetyDBContext.cs	Replace constructor; use DbContextOptions<T>
All 31 *ETC.cs files	EntityTypeConfiguration<T> → IEntityTypeConfiguration<T>
All 14 migrations + Configuration.cs	Delete all; regenerate baseline
GenericRepository.cs	Inject DbContext via constructor (remove new OpenSafetyDBContext())
EFUnitOfWork.cs	Inject DbContext via constructor
EFDicoRepository.cs	Fix LINQ-to-SQL patterns (remove .ToList() before filter)
Generate New EF Core Migration:
dotnet ef migrations add InitialCreate \
  --project OPenSafetyInfrastructure \
  --startup-project OpenSafetyDistributedService
  Sprint 2.2: OPenSafetyInfrastructure - Elasticsearch 8 (5 days)
NEST 6 → Elastic.Clients.Elasticsearch 8:
WebApiElasticSearch.cs (2,132 lines) requires complete rewrite:
Old NEST 6 API	New Elastic 8 API
new ConnectionSettings(uri)	new ElasticsearchClientSettings(uri)
client.Search<T>(s => s.Query(...))	await client.SearchAsync<T>(s => s.Query(...))
response.IsValid	response.IsSuccess()
Replace ASMX Web Reference:
•	Delete Web References/MdmWS/ folder
•	Rewrite WSMdmRepository using IHttpClientFactory
Fix HttpClient Anti-patterns:

// Before (13 files)
using (var client = new HttpClient()) { var result = client.GetAsync(url).Result; }

// After
private readonly HttpClient _client;
public Service(HttpClient client) => _client = client;
public async Task<T> GetDataAsync() => await _client.GetFromJsonAsync<T>(...);
Sprint 2.3: OpenSafetyApplication (4 days)
Changes Required:
Component	Change
SecurityService.cs	Replace HttpContext.Current.Session with IHttpContextAccessor + ISession
AutoMapperConfig.cs	Remove static Mapper.Initialize(); use Profile-based configuration
All services	Replace log4net with ILogger<T> (50 files)
All services	Replace ConfigurationManager.AppSettings with IConfiguration (27 files)
AutoMapper 5 → 13 Migration:
// Before
Mapper.Initialize(cfg => cfg.CreateMap<BlocDTO, Bloc>());
var result = Mapper.Map<Bloc>(dto);

// After
public class DicoProfile : Profile {
    public DicoProfile() { CreateMap<BlocDTO, Bloc>(); }
}
// Program.cs: services.AddAutoMapper(typeof(DicoProfile).Assembly);
// Service: private readonly IMapper _mapper;
var result = _mapper.Map<Bloc>(dto);
Deliverables:
•	[ ] Infrastructure builds on .NET 8; EF Core migration validated
•	[ ] Elasticsearch client rewritten with v8 API
•	[ ] All HttpClient anti-patterns eliminated
•	[ ] Application layer builds; AutoMapper 13 configured
•	[ ] Git tag: phase2-complete
---
Phase 3: API Host - WCF → ASP.NET Core Web API (Weeks 9-12 - 16 days)
Replace all 8 WCF services with REST API controllers
Sprint 3.1: Dissolve OpenSafetyDependancyResolver (1 day)
Translate all Unity registrations to services.AddScoped<I, T>() in new Program.cs
Sprint 3.2: Create Program.cs for DistributedService (2 days)
Full middleware pipeline:
var builder = WebApplication.CreateBuilder(args);

// Database
builder.Services.AddDbContext<OpenSafetyDBContext>(opt =>
    opt.UseSqlServer(builder.Configuration.GetConnectionString("OpenSafetyDBContext"))
       .UseLazyLoadingProxies());

// Repositories
builder.Services.AddScoped<IDicoRepository, EFDicoRepository>();
builder.Services.AddScoped<IAcquisitionRepository, EFDicoRepository>();
builder.Services.AddScoped(typeof(IGenericRepository<>), typeof(GenericRepository<>));
builder.Services.AddScoped<IUnitOfWork, EFUnitOfWork>();

// External API clients
builder.Services.AddHttpClient<WSMdmRepository>();
builder.Services.AddHttpClient<WSCosmetochemRepository>();
builder.Services.AddScoped<IMdmRepository, WSMdmRepository>();
builder.Services.AddScoped<ICosmetochemRepository, WSCosmetochemRepository>();

// Application Services
builder.Services.AddScoped<IDicoService, DicoApplicationService>();
builder.Services.AddScoped<IAdminService, AdminApplicationService>();
// ... 7 more services

// AutoMapper
builder.Services.AddAutoMapper(typeof(DicoApplicationService).Assembly);

// Auth
builder.Services.AddAuthentication(NegotiateDefaults.AuthenticationScheme).AddNegotiate();
builder.Services.AddAuthorization();

// ASP.NET Core + Swagger
builder.Services.AddControllers();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// DB migration at startup
using (var scope = app.Services.CreateScope())
    scope.ServiceProvider.GetRequiredService<OpenSafetyDBContext>().Database.Migrate();

app.UseSwagger();
app.UseSwaggerUI();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
Sprint 3.3: Create 8 ASP.NET Core Controllers (8 days)
WCF → REST Mapping:
WCF Service	New Controller	Route	Methods
OpenSafetyDicoWCFService	DicoController	api/dico	15 endpoints
OpenSafetyAdminWCFService	AdminController	api/admin	28 endpoints
OpenSafetyAcquisitionWCFService	AcquisitionController	api/acquisition	12 endpoints
OpenSafetyDataWCFService	DataController	api/data	18 endpoints
OpenSafetyCosmetochemWCFService	CosmetochemController	api/cosmetochem	8 endpoints
OpenSafetyMdmWCFService	MdmController	api/mdm	6 endpoints
OpenSafetyMpnetWCFService	MpnetController	api/mpnet	7 endpoints
OpenSafetySynonymsWCFService	SynonymsController	api/synonyms	4 endpoints
Pattern:
// Replace: OpenSafetyDicoWCFService.svc.cs (1,006 lines)
// With: DicoController.cs

[ApiController]
[Route("api/dico")]
[Authorize]
public class DicoController : ControllerBase
{
    private readonly IDicoService _dicoService;
    private readonly ILogger<DicoController> _logger;

    public DicoController(IDicoService dicoService, ILogger<DicoController> logger)
    {
        _dicoService = dicoService;
        _logger = logger;
    }

    // WCF: [WebGet(UriTemplate = "GetAllSource/{domain}/{loginNT}")]
    [HttpGet("GetAllSource/{domain}/{loginNT}")]
    public ActionResult<ResponseSourceDTO> GetAllSource(string domain, string loginNT)
        => Ok(_dicoService.GetAllSource(domain, loginNT));
}
Sprint 3.4: Delete WCF Artifacts (0.5 day)
Files to remove:
•	All 8 .svc + .svc.cs files
•	Global.asax + Global.asax.cs
•	Web.config
•	App_Start/UnityConfig.cs
Sprint 3.5: Deploy & Test (1 day)
dotnet publish OpenSafetyDistributedService -c Release -o ./publish/api

# Deploy to IIS (parallel to WCF)
# New: https://dev-server/opensafety-api/swagger
# Old: https://dev-server/OpenSafetyWS/*.svc
Smoke test all 8 controllers via Swagger UI
Deliverables:
•	[ ] All 8 WCF services replaced with API controllers
•	[ ] Program.cs bootstraps full pipeline
•	[ ] appsettings.json created (no secrets)
•	[ ] New API deployed to dev; Swagger UI functional
•	[ ] All endpoints return 200 OK with valid JSON
•	[ ] Git tag: phase3-complete
---
Phase 4: Frontend - MVC 5 → ASP.NET Core MVC (Weeks 13-19 - 29 days)
Largest scope: 14 MVC controllers, 11 API controllers, 119 Razor views
Sprint 4.1: Delete Legacy Artifacts (1 day)
Remove:
•	Global.asax + Global.asax.cs
•	Web.config
•	App_Start/ folder (BundleConfig, FilterConfig, RouteConfig, WebApiConfig)
•	All 6 Service References/ folders (WCF proxies)
Sprint 4.2: Create Program.cs for Frontend (2 days)
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews();
builder.Services.AddHttpContextAccessor();

// Session
builder.Services.AddSession(opt => {
    opt.IdleTimeout = TimeSpan.FromHours(8);
    opt.Cookie.HttpOnly = true;
});

// Typed HTTP clients → OpenSafety API
builder.Services.AddHttpClient<DicoApiClient>(c =>
    c.BaseAddress = new Uri(builder.Configuration["Endpoints:DicoApi"]!));
builder.Services.AddHttpClient<AdminApiClient>(c =>
    c.BaseAddress = new Uri(builder.Configuration["Endpoints:AdminApi"]!));
// ... 4 more clients

// AutoMapper, Auth, etc.
builder.Services.AddAutoMapper(typeof(Program).Assembly);
builder.Services.AddAuthentication(NegotiateDefaults.AuthenticationScheme).AddNegotiate();

var app = builder.Build();

app.UseExceptionHandler("/OpsError/Index");
app.UseStaticFiles();
app.UseSession();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllerRoute(name: "areas", pattern: "{area:exists}/{controller=Home}/{action=Index}/{id?}");
app.MapControllerRoute(name: "default", pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
Sprint 4.3: Create 6 Typed HttpClient Classes (2 days)
Replace WCF proxies:
public class DicoApiClient
{
    private readonly HttpClient _client;
    public DicoApiClient(HttpClient client) => _client = client;

    public async Task<ResponseSourceDTO?> GetAllSourceAsync(string domain, string loginNT)
        => await _client.GetFromJsonAsync<ResponseSourceDTO>(
               $"GetAllSource/{Uri.EscapeDataString(domain)}/{Uri.EscapeDataString(loginNT)}");
}
Sprint 4.4: Migrate All Controllers (3 days)
14 MVC Controllers:
// Replace in every controller
using System.Web.Mvc → using Microsoft.AspNetCore.Mvc
HttpContext.Current → _httpContextAccessor.HttpContext
Session["key"] → HttpContext.Session.GetString("key")
new ServiceDico.DicoServiceClient() → await _dicoApiClient.GetAllSourceAsync()
ConfigurationManager.AppSettings["key"] → _configuration["key"]
log4net → ILogger<T>
11 Web API Controllers:
using System.Web.Http → using Microsoft.AspNetCore.Mvc
: ApiController → : ControllerBase
Add [ApiController] attribute
IHttpActionResult → IActionResult
Sprint 4.5: Update 119 Razor Views (5 days)
Systematic procedure:
1.	Namespace fixes (find & replace):
@using System.Web.Mvc → @using Microsoft.AspNetCore.Mvc
2.	@model directive fixes (12+ views):
@model OpenSafetyFrontend.ServiceAdmin.BlocDTO
→ @model OpenSafety.Contract.BlocDico.BlocDTO
3.	Ajax helpers:
•	Ensure jquery.unobtrusive-ajax.js included via LibMan
4.	PagedList:
@using PagedList.Mvc → @using X.PagedList.Mvc.Core
Sprint 4.6: Migrate jqGrid → DataTables.js (3 days)
7 views affected:
•	Admin: Blocs, Colonnes, Sources, BlocVersionMetas, Metas
•	Home: SearchNoSql, Index (partial grid)
Replacement pattern:
<!-- Before (jqGrid server-side) -->
@Html.Trirand().JQGrid(Model.GridModel, "GridId")

<!-- After (DataTables.js client-side) -->
<table id="GridId" class="table table-striped"></table>
<script>
$('#GridId').DataTable({
    ajax: '/api/admin/GetBlocs',
    columns: [
        { data: 'NAME_EN', title: 'Name EN' },
        { data: 'NAME_FR', title: 'Name FR' }
    ],
    pageLength: 25
});
</script>
Sprint 4.7: Replace BundleConfig with LibMan (1 day)
// libman.json
{
  "version": "1.0",
  "defaultProvider": "cdnjs",
  "libraries": [
    { "library": "bootstrap@5.3.3", "destination": "wwwroot/lib/bootstrap" },
    { "library": "jquery@3.7.1", "destination": "wwwroot/lib/jquery" },
    { "library": "datatables@2.1.8", "destination": "wwwroot/lib/datatables" }
  ]
}
Move custom JS: Scripts/ops_js/*.js → wwwroot/js/ops/*.js
Sprint 4.8: End-to-End Smoke Test (1.5 days)
Test matrix:
•	✅ Home: search, results, silico launch
•	✅ Acquisition: create/edit
•	✅ Admin: all 6 CRUD modules
•	✅ Language switching
•	✅ Windows Authentication
•	✅ Excel/CSV export
•	✅ MarvinJS chemical sketcher
Deliverables:
•	[ ] Frontend builds on .NET 8
•	[ ] All 6 WCF proxies replaced with typed HttpClient
•	[ ] All 25 controllers updated
•	[ ] All 119 views compile
•	[ ] 7 jqGrid views migrated to DataTables
•	[ ] E2E test matrix passes on DEV
•	[ ] Git tag: phase4-complete
---
Phase 5: Background Services (Week 20 - 6 days)
Sprint 5.1: WsAsynchronousSilicoState → Worker Service (3 days)
Replace ServiceBase with BackgroundService:
public class OpenSafetyWorkerService : BackgroundService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ILogger<OpenSafetyWorkerService> _logger;
    private readonly IConfiguration _configuration;

    public OpenSafetyWorkerService(IHttpClientFactory factory, ILogger<OpenSafetyWorkerService> logger, IConfiguration config)
    {
        _httpClientFactory = factory;
        _logger = logger;
        _configuration = config;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromSeconds(30));

        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            try
            {
                var client = _httpClientFactory.CreateClient("CosmetochemApi");
                var response = await client.GetAsync("AnalyzeSilicoResult/...", stoppingToken);
                response.EnsureSuccessStatusCode();
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                _logger.LogError(ex, "Error in background job");
            }
        }
    }
}
Delete:
•	ProjectInstaller.cs/Designer.cs/resx
•	OpenSafetyAsynchronousService.Designer.cs
•	Old Program.cs
Sprint 5.2: OpenSafetyStateChecker (1 day)
Options:
•	Option A (recommended): Retire (empty stub with no logic)
•	Option B: Convert to health-check worker using IHealthChecks
Sprint 5.3: Update JsonToSql (0.5 day)
<!-- Bump from netcoreapp3.1 -->
<TargetFramework>net8.0</TargetFramework>
Replace Microsoft.Office.Interop.Excel with ClosedXML
Sprint 5.4: Retire ConsoleTest (0.5 day)
Recommended: Remove from solution (developer scratch tool)
Deliverables:
•	[ ] WsAsynchronousSilicoState runs as .NET 8 Worker Service
•	[ ] PeriodicTimer replaces System.Timers.Timer
•	[ ] Service polls API successfully in DEV
•	[ ] JsonToSql targets .NET 8
•	[ ] Git tag: phase5-complete
---
Phase 6: Test Modernization (Week 21 - 9 days)
Sprint 6.1: Convert to xUnit (2 days)
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.8" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.1" />
    <PackageReference Include="Moq" Version="4.20.72" />
    <PackageReference Include="FluentAssertions" Version="6.12.1" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
  </ItemGroup>
</Project>
Migration:
// Replace
[TestClass] → remove
[TestMethod] → [Fact]
Assert.AreEqual(x, y) → x.Should().Be(y)
Assert.IsNotNull(x) → x.Should().NotBeNull()
Sprint 6.2: Write Unit Tests (3 days)
Priority classes:
Test Class	SUT	Mock
SecurityServiceTests	CheckSecurityService()	IMdmRepository, IHttpContextAccessor
DicoApplicationServiceTests	GetAllSource(), CreateSource()	IDicoRepository, IMapper
AcquisitionApplicationServiceTests	GetJobs(), CreateJob()	IAcquisitionRepository
EFDicoRepositoryTests	GetAllBlocs()	In-memory EF Core
AdminApplicationServiceTests	Bloc CRUD	IGenericRepository<Bloc>
Sprint 6.3: Write Integration Tests (3 days)
public class DicoControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public DicoControllerTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
            builder.ConfigureServices(services => {
                services.RemoveAll<DbContextOptions<OpenSafetyDBContext>>();
                services.AddDbContext<OpenSafetyDBContext>(opt =>
                    opt.UseInMemoryDatabase("TestDb"));
            })).CreateClient();
    }

    [Fact]
    public async Task GetAllSource_Returns200()
    {
        var response = await _client.GetAsync("/api/dico/GetAllSource/loreal/testuser");
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
}
Sprint 6.4: Configure CI Coverage Gate (1 day)
// Jenkinsfile
stage('Test & Coverage') {
    steps {
        bat '''
        dotnet test OpenSafety.sln \
          --collect:"XPlat Code Coverage" \
          --logger "trx"
        '''
    }
}
Deliverables:
•	[ ] Both test projects use xUnit + Moq + FluentAssertions
•	[ ] ≥5 unit test classes
•	[ ] ≥8 integration tests
•	[ ] Coverage gate set at 60%
•	[ ] Git tag: phase6-complete
---
Phase 7: CI/CD & Deployment (Week 22 - 4 days)
Sprint 7.1: Update Jenkinsfiles (1 day)
Replace MSBuild with dotnet CLI:
pipeline {
    stages {
        stage('Restore') { steps { bat 'dotnet restore OpenSafety.sln' } }
        stage('Build') { steps { bat 'dotnet build OpenSafety.sln -c Release --no-restore' } }
        stage('Test') { steps { bat 'dotnet test OpenSafety.sln -c Release --no-build --logger trx' } }
        stage('Publish API') { steps { bat 'dotnet publish OpenSafetyDistributedService -c Release -o publish\\api' } }
        stage('Migrate DB') {
            steps {
                bat '''
                dotnet ef database update ^
                  --project OPenSafetyInfrastructure ^
                  --startup-project OpenSafetyDistributedService
                '''
            }
        }
        stage('Deploy to IIS') { steps { deployDotNetWithParams(publishDir: 'publish\\api', siteName: 'OpenSafety-API') } }
    }
}
Sprint 7.2: IIS Configuration (2 days)
Per environment (dev, pit, int, prod):
1.	Install .NET 8 Windows Hosting Bundle:
•	Download: https://dotnet.microsoft.com/download/dotnet/8.0
•	Restart IIS: iisreset
2.	Configure Application Pools:
.NET CLR Version: No Managed Code
   Managed Pipeline Mode: Integrated
3.	Add web.config:
<system.webServer>
  <handlers>
    <add name="aspNetCore" path="*" verb="*" modules="AspNetCoreModuleV2" />
  </handlers>
  <aspNetCore processPath="dotnet"
              arguments=".\OpenSafetyDistributedService.dll"
              stdoutLogEnabled="true"
                 hostingModel="inprocess" />
   </system.webServer>
4.	Azure Key Vault:
// Program.cs
builder.Configuration.AddAzureKeyVault(
    new Uri(config["KeyVaultUri"]!), 
       new DefaultAzureCredential());
       Sprint 7.3: Decommission WCF (0.5 day)
After all consumers migrated:
1.	Take WCF app pool offline
2.	Monitor for .svc requests for 2 weeks
3.	Archive WCF deployment artifacts
Sprint 7.4: Production Go-Live (0.5 day)
Checklist:
•	[ ] DB backup taken
•	[ ] EF Core migration dry-run on prod replica
•	[ ] Canary deployment to 1 IIS node
•	[ ] Rollback plan documented
•	[ ] .NET 8 Hosting Bundle on all servers
•	[ ] App pools reconfigured
•	[ ] API + Frontend published
•	[ ] dotnet ef database update executed
•	[ ] Logs flowing to Application Insights
•	[ ] Smoke tests pass
Deliverables:
•	[ ] Jenkins pipelines use dotnet CLI
•	[ ] .NET 8 Hosting Bundle on all environments
•	[ ] Azure Key Vault configured
•	[ ] WCF offline after monitoring period
•	[ ] Git tag: phase7-complete
•	[ ] Merge feature/dotnet8-migration → master
---
7. Risk Assessment & Mitigation
7.1 Critical Risks
Risk	Probability	Impact	Mitigation
External WCF consumers break	🔴 High	🔴 Critical	Strangler Fig: Run WCF + REST in parallel; audit all consumers before cutover
Elasticsearch cluster incompatible	🔴 High	🔴 High	Upgrade ES cluster to 8.x first; or use NEST 7.x as intermediate
EF Core migration schema mismatch	🟡 Medium	🔴 High	Run dotnet ef dbcontext scaffold against prod DB; compare schemas
Credentials leaked in Git history	🔴 High	🔴 Critical	IMMEDIATE: Rotate all credentials; rewrite Git history with BFG
HttpClient socket exhaustion in prod	🟡 Medium	🔴 High	Load test before prod deployment; verify IHttpClientFactory usage
7.2 Medium Risks
Risk	Probability	Impact	Mitigation
Trirand.jqGrid no replacement	🔴 High	🟡 Medium	Dedicate UI sprint; migrate to DataTables.js; agree on feature parity
AutoMapper 5→13 unmapped config	🔴 High	🟡 Medium	Run cfg.AssertConfigurationIsValid() in startup tests
Windows Auth (Negotiate) behavior differs	🟡 Medium	🔴 High	Test on staging IIS with .NET 8 Hosting Bundle before prod
Razor views namespace/tag helper errors	🟡 Medium	🟡 Medium	Run dotnet build after conversion; fix systematically
---
8. Effort & Timeline Summary
8.1 Single Developer (Sequential)
Phase	Sprints	Weeks	Effort (days)
0 - Preparation	0	1	5
1 - Foundation Libraries	1	2	6
2 - Infrastructure + Application	2-3	3	17
3 - API Host	4-5	2	16
4 - Frontend	6-9	4	29
5 - Background Services	10	1	6
6 - Tests	11	1	9
7 - CI/CD + Deploy	11	1	4
Total	11	15	92
Calendar Time: ~22 weeks (with buffer for testing/stabilization)
8.2 Two Developers (Parallel Tracks)
Track A (Developer 1): Infrastructure + Backend
•	Phase 0: 5 days
•	Phase 1: 6 days
•	Phase 2: 17 days
•	Phase 3: 16 days
•	Subtotal: 44 days
Track B (Developer 2): Frontend (starts after Phase 3 API stable)
•	Phase 4: 29 days (starts Week 9)
•	Phase 5: 6 days
•	Subtotal: 35 days
Shared: Phases 6-7 (both developers)
•	Phase 6: 9 days
•	Phase 7: 4 days
Total Parallel Effort: ~55 developer-days
Calendar Time: ~12-14 weeks
---
9. Success Criteria
9.1 Technical Criteria
•	[ ] All 12 active projects build on .NET 8 with 0 errors
•	[ ] All 8 WCF services replaced with REST API endpoints
•	[ ] All 119 Razor views render without errors
•	[ ] Database schema matches production after EF Core migration
•	[ ] All typed HttpClient instances use IHttpClientFactory
•	[ ] No plaintext secrets in source code or config files
•	[ ] Code coverage ≥ 60%
•	[ ] All Swagger API endpoints return 200 OK in dev/staging
9.2 Operational Criteria
•	[ ] Jenkins pipelines build/test/deploy successfully
•	[ ] IIS hosting on .NET 8 verified in all environments
•	[ ] Windows Authentication (Negotiate) functional
•	[ ] Session state persists across requests
•	[ ] Background service polls API successfully
•	[ ] WCF endpoints offline after 2-week monitoring period
•	[ ] No .svc requests logged after cutover
•	[ ] Application Insights logs flowing
9.3 Business Criteria
•	[ ] All functional smoke tests pass
•	[ ] End-users can perform all CRUD operations
•	[ ] Chemical structure search (MarvinJS) functional
•	[ ] Excel/CSV export works
•	[ ] Multi-language support works
•	[ ] No production incidents in first 2 weeks post-deployment
---
10. Rollback Plan
If critical issues discovered post-deployment:
1.	Immediate (< 5 minutes):
•	Switch IIS app pool back to WCF virtual directory
•	Restart application pools
2.	Database rollback (< 30 minutes):
•	Restore database from pre-migration backup
•	Verify WCF endpoints functional
3.	Communication:
•	Notify all stakeholders
•	Document root cause
•	Schedule fix + re-deployment
Prerequisites for rollback capability:
•	[ ] Full database backup taken immediately before migration
•	[ ] WCF IIS virtual directory archived (not deleted)
•	[ ] WCF endpoints remain deployed for 2 weeks minimum
•	[ ] Rollback procedure tested in staging environment
---
11. Post-Migration Optimization Opportunities
Not required for initial .NET 8 migration, but recommended for future work:
11.1 Code Quality Improvements
•	Enable nullable reference types globally (<Nullable>enable</Nullable>)
•	Convert all blocking .Result calls to async/await (currently only 3 files use async)
•	Decompose "God classes" (e.g., CosmetochemApplicationService at 2,208 lines)
•	Remove French/English mixed comments and error messages
•	Implement global exception handler middleware (remove 100+ duplicate try/catch blocks)
11.2 Architecture Modernization
•	Replace Repository/UnitOfWork pattern with MediatR + CQRS
•	Migrate from Sessions to JWT authentication tokens
•	Implement API versioning (/api/v2/dico/...)
•	Add response caching with Redis
•	Implement rate limiting on API endpoints
11.3 Performance Optimization
•	Add compiled queries for EF Core hot paths
•	Implement database query result caching
•	Add response compression middleware
•	Optimize LINQ queries (push filters to database)
•	Add database indexes based on query analyzer output
11.4 DevOps Improvements
•	Containerize with Docker + Kubernetes
•	Implement blue/green deployments
•	Add synthetic monitoring (Application Insights availability tests)
•	Set up automated performance regression testing
•	Implement feature flags for gradual rollouts
---
12. Appendices
Appendix A: Complete File Change Inventory
Files requiring modification:
•	225 source files reference incompatible APIs (39% of codebase)
•	119 Razor views require namespace/model updates
•	50 files use log4net (replace with ILogger<T>)
•	27 files use ConfigurationManager (replace with IConfiguration)
•	13 files instantiate HttpClient directly (replace with IHttpClientFactory)
•	31 Entity Type Configuration classes (EF6 → EF Core API)
•	14 EF6 migration files (delete; regenerate as 1 baseline)
Appendix B: External Dependencies
Third-party services the application integrates with:
•	Elasticsearch cluster (version 6.x → must upgrade to 8.x)
•	MDM Web Service (ASMX SOAP)
•	Cosmetochem API (HTTP/JSON)
•	MPnet API (HTTP/JSON)
•	Synonyms API (HTTP/JSON)
•	MarvinJS chemical structure editor (CDN, JavaScript only)
Impact: All external service clients must be rewritten to use IHttpClientFactory
Appendix C: Deployment Topology
Current production environment:
•	Web Tier: 2 IIS servers (load balanced)
•	API Tier: 2 IIS servers (load balanced)
•	Database: Azure SQL Database (Standard S3)
•	Search: Elasticsearch 6.x cluster (3 nodes)
•	Background Service: 1 Windows Server running Windows Service
Post-migration:
•	Same infrastructure
•	.NET 8 Windows Hosting Bundle required on all 5 servers
•	IIS app pools reconfigured to "No Managed Code"
Appendix D: Key Contacts
Stakeholders to coordinate with:
•	DBA: Database credential rotation, backup/restore, migration validation
•	Network/Security: Azure Key Vault access, firewall rules for new API endpoints
•	External Teams: Notification of WCF → REST migration timeline
•	QA Team: End-to-end smoke test execution, UAT coordination
•	DevOps: Jenkins pipeline updates, IIS configuration changes
---
13. Conclusion & Recommendations
13.1 Immediate Actions (Week 1)
1.	🔴 CRITICAL: Rotate exposed credentials and rewrite Git history
2.	Fix Infrastructure→Frontend layer violation
3.	Remove 4 stub projects from solution
4.	Get executive approval for 12-22 week timeline
13.2 Recommended Approach
•	Use Strangler Fig pattern: Deploy new .NET 8 API alongside WCF
•	Parallel development tracks: 2 developers can reduce timeline from 22 → 13 weeks
•	Continuous testing: Run smoke tests after each phase completion
•	Gradual cutover: Migrate internal consumers first, then external
13.3 Go/No-Go Decision Factors
Proceed with migration if:
•	✅ Executive commitment to 12-22 week timeline
•	✅ 2 senior developers allocated full-time
•	✅ DBA available for EF Core migration validation
•	✅ Elasticsearch cluster can be upgraded to 8.x
•	✅ External WCF consumers agree to migration timeline
Delay migration if:
•	❌ Critical business deadlines in next 6 months conflict
•	❌ External WCF consumers cannot migrate within 6 months
•	❌ Elasticsearch cluster upgrade not approved
•	❌ Only 1 developer available (22-week timeline unacceptable)
13.4 Final Recommendation
Proceed with migration using the phased approach outlined in this plan. The technical debt and security risks of remaining on .NET Framework 4.7.1 with exposed credentials outweigh the cost of migration. The Strangler Fig pattern minimizes deployment risk while providing a clear rollback path.
Prioritize:
1.	Credential rotation (Week 1)
2.	Infrastructure/Application layers (Weeks 2-8)
3.	API migration with parallel WCF (Weeks 9-12)
4.	Frontend migration (Weeks 13-19)
This approach ensures the highest-risk components (database, service layer) are stabilized before migrating the user-facing frontend.
---
Document Version: 1.0
Last Updated: 2024
Status: Final - Approved for Implementation
---
This report synthesizes analysis from:
•	Audit.md - Detailed modernization assessment
•	Upgrade_report.md - Technical migration guide
•	answers.md - Solution analysis questionnaire
•	Plan.md - Execution roadmap



