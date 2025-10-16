using System.Diagnostics;
using System.Text;
using System.Text.Json;

namespace RandomLocationWinForm
{
    public static class ControlExtensions
    {
        public static Task InvokeAsync(this Control control, Func<Task> func)
        {
            var tcs = new TaskCompletionSource();
            control.BeginInvoke(async () =>
            {
                try { await func(); tcs.SetResult(); }
                catch (Exception ex) { tcs.SetException(ex); }
            });
            return tcs.Task;
        }
    }
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private bool _loaded;

        private async void Form1_Load(object? sender, EventArgs e)
        {
            await webView21.EnsureCoreWebView2Async();

            var tcs = new TaskCompletionSource();
            webView21.CoreWebView2.DOMContentLoaded += (s, ev) =>
            {
                if (!_loaded) { _loaded = true; tcs.TrySetResult(); }
            };

            var htmlPath = Path.Combine(Application.StartupPath, "leaflet.html");
            webView21.Source = new Uri(htmlPath);
            await tcs.Task;

            var workingDir = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, @"..\..\..\..\GeoPandas"));
            var scriptPath = Path.Combine(workingDir, "GeoPandasTest.py");
            // 로드 완료 후 마커 추가
            webView21.NavigationCompleted += async (_, __) =>
            {
                //await webView21.ExecuteScriptAsync(
                //    "addMarker(37.5665,126.9780,'서울');");
                //await webView21.ExecuteScriptAsync(
                //    "addMarker(35.1796,129.0756,'부산');");

                // GeoJSON 예시(FeatureCollection)
                var geojson = JsonSerializer.Serialize(new
                {
                    type = "FeatureCollection",
                    features = new[] {
                    new {
                        type = "Feature",
                        geometry = new { type = "LineString",
                            coordinates = new[] {
                                new[] {126.9780, 37.5665}, // [lon,lat]
                                new[] {129.0756, 35.1796}
                            }
                        },
                        properties = new { name = "서울-부산" }
                    }
                }
                });
                //await webView21.ExecuteScriptAsync($"addGeoJson({geojson})");
            };

            //var pt = await RunPythonAndGetPointAsync(
            //    fileName: "python",
            //    //arguments: $"-m debugpy --listen 127.0.0.1:5678 --wait-for-client -u \"{scriptPath}\"",
            //    arguments: $"-u \"{scriptPath}\"",
            //    workingDir: workingDir
            //);

            //if (pt is not null)
            //{
            //    // 3) 지도에 표시
            //    var label = JsonSerializer.Serialize(pt.name ?? "Point");
            //    await webView21.ExecuteScriptAsync($"setCenter({pt.lat}, {pt.lon}, 13)");
            //    await webView21.ExecuteScriptAsync($"addMarker({pt.lat}, {pt.lon}, {label})");
            //}
            //else
            //{
            //    MessageBox.Show("파이썬에서 좌표를 받지 못했습니다.");
            //}

            await RunPythonAndStreamPointsAsync(
                fileName: "python",
                //arguments: $"-m debugpy --listen 127.0.0.1:5678 --wait-for-client -u \"{scriptPath}\"",
                arguments: $"-u \"{scriptPath}\"",
                workingDir: workingDir
            );
        }
        private record PointDto(double lat, double lon, string? name);
        private async Task<PointDto?> RunPythonAndGetPointAsync(string fileName, string arguments, string workingDir)
        {
            var psi = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = arguments,
                WorkingDirectory = workingDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                // UTF-8 강제 (Windows에서 한글 안전)
            };
            // 파이썬 전체를 UTF-8 모드로
            psi.EnvironmentVariables["PYTHONUTF8"] = "1";

            using var p = new Process { StartInfo = psi };
            var output = new StringBuilder();
            var error = new StringBuilder();
            p.OutputDataReceived += (_, e) => { if (e.Data != null) output.AppendLine(e.Data); };
            p.ErrorDataReceived += (_, e) => { if (e.Data != null) error.AppendLine(e.Data); };

            if (!p.Start())
                return null;

            p.BeginOutputReadLine();
            p.BeginErrorReadLine();

            // 타임아웃은 상황에 맞게 (여기선 10초)
            if (!p.WaitForExit(10_000))
            {
                try { p.Kill(); } catch { /* ignore */ }
                return null;
            }

            // ✅ Python이 JSON 한 줄만 출력하도록 가정
            var jsonLine = output.ToString().Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries).LastOrDefault();
            if (string.IsNullOrWhiteSpace(jsonLine))
            {
                Debug.WriteLine("STDERR: " + error);
                return null;
            }

            try
            {
                var dto = JsonSerializer.Deserialize<PointDto>(jsonLine);
                return dto;
            }
            catch (Exception ex)
            {
                Debug.WriteLine("JSON 파싱 실패: " + ex.Message + "\nRAW: " + jsonLine);
                return null;
            }
        }

        private async Task RunPythonAndStreamPointsAsync(string fileName, string arguments, string workingDir)
        {
            var psi = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = arguments,
                WorkingDirectory = workingDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8
            };
            psi.EnvironmentVariables["PYTHONUTF8"] = "1";

            using var p = new Process { StartInfo = psi };
            p.Start();

            // ✅ 비동기 읽기 — 실시간으로 한 줄씩 수신
            while (!p.HasExited)
            {
                string? line = await p.StandardOutput.ReadLineAsync();
                if (line == null) break;

                try
                {
                    var pt = JsonSerializer.Deserialize<PointDto>(line);
                    if (pt != null)
                    {
                        // 메인 스레드에서 WebView2 조작
                        await this.InvokeAsync(async () =>
                        {
                            var label = JsonSerializer.Serialize(pt.name ?? "Point");
                            await webView21.ExecuteScriptAsync($"updateMarker({pt.lat}, {pt.lon}, {label})");
                        });
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"JSON 파싱 오류: {ex.Message} / {line}");
                }
            }

            // 남은 에러 메시지 출력 (선택)
            string err = await p.StandardError.ReadToEndAsync();
            if (!string.IsNullOrWhiteSpace(err))
                Debug.WriteLine("Python stderr:\n" + err);
        }
    }
}
