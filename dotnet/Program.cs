using System.Diagnostics;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Habilitar CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAllOrigins",
        builder =>
        {
            builder.AllowAnyOrigin()
                   .AllowAnyMethod()
                   .AllowAnyHeader();
        });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Usar CORS
app.UseCors("AllowAllOrigins");

app.MapPost("/recommendations", async (HttpRequest request) =>
{
    var requestContent = await new StreamReader(request.Body).ReadToEndAsync();
    var process = new Process
    {
        StartInfo = new ProcessStartInfo
        {
            FileName = "/home/app/venv/bin/python",
            Arguments = "/home/app/process.py",
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        }
    };

    process.Start();

    await process.StandardInput.WriteLineAsync(requestContent);
    process.StandardInput.Close();

    var result = await process.StandardOutput.ReadToEndAsync();
    var errors = await process.StandardError.ReadToEndAsync();

    process.WaitForExit();

    if (!string.IsNullOrEmpty(errors))
    {
        return Results.Problem(errors);
    }

    return Results.Content(result, "application/json");
});

// Agregar el endpoint de health check
app.MapGet("/health", () => Results.Ok("Service is running"));

app.Run();
