using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing.Drawing2D;
using System.Text;
using System.Text.Json;

namespace RandomLocationWinForm
{
    public partial class MainWindow : Form
    {
        public MainWindow()
        {
            InitializeComponent();

            menuStrip1.BackColor = Color.FromArgb(240, 240, 240);

            menuStrip1.Margin = new Padding(0);
            menuStrip1.Padding = new Padding(5, 3, 5, 2);
            menuStrip1.ForeColor = Color.Black;

            //Panel line = new Panel();
            //line.Dock = DockStyle.Top;
            //line.Height = 1;
            //line.BackColor = Color.FromArgb(200, 200, 200); // 옅은 회색 라인
            //this.Controls.Add(line);
            //line.BringToFront();

            // 메뉴바 아래 경계선 (밝은 선)
            Panel borderBottom = new Panel();
            borderBottom.Dock = DockStyle.Top;
            borderBottom.Height = 1;
            borderBottom.BackColor = Color.FromArgb(220, 220, 220);
            this.Controls.Add(borderBottom);
            borderBottom.BringToFront();

            // 메뉴바 위 경계선 (살짝 어두운 선)
            Panel borderTop = new Panel();
            borderTop.Dock = DockStyle.Top;
            borderTop.Height = 1;
            borderTop.BackColor = Color.FromArgb(180, 180, 180);
            this.Controls.Add(borderTop);
            borderTop.BringToFront();

            borderTop.SendToBack();
            this.Controls.SetChildIndex(borderTop, 0);
            this.Controls.SetChildIndex(menuStrip1, 1);
            this.Controls.SetChildIndex(borderBottom, 2);
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
        }
        private record PointDto(double lat, double lon, string? name);
        private async Task<PointDto?> RunPythonAndGetPointAsync(string fileName, string arguments, string workingDir)
        {
            var psi = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = $"-X utf8" + arguments,
                WorkingDirectory = workingDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
            };
            psi.EnvironmentVariables["PYTHONUTF8"] = "1";
            psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

            using var p = new Process { StartInfo = psi };
            p.Start();

            string output = await p.StandardOutput.ReadToEndAsync();
            string error = await p.StandardError.ReadToEndAsync();

            await p.WaitForExitAsync();

            var jsonLine = output.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries).LastOrDefault();
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

        private async Task<(PointDto? point, string? label)> RunPythonAndStreamPointsAsync(string pythonExe, string scriptPath, string workingDir)
        {
            var psi = new ProcessStartInfo
            {
                FileName = pythonExe,
                Arguments = $"-X utf8 -u \"{scriptPath}\"",
                WorkingDirectory = workingDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8
            };
            psi.EnvironmentVariables["PYTHONUTF8"] = "1";
            psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

            using var p = new Process { StartInfo = psi };
            p.Start();

            PointDto? lastCoord = null;
            string? lastLabel = null;

            while (!p.HasExited)
            {
                string? line = await p.StandardOutput.ReadLineAsync();
                if (line == null) break;

                try
                {
                    var pt = JsonSerializer.Deserialize<PointDto>(line);
                    if (pt != null)
                    {
                        lastCoord = pt;
                        await this.InvokeAsync(async () =>
                        {
                            var label = JsonSerializer.Serialize(pt.name ?? "Point");
                            lastLabel = label;

                            await webView21.ExecuteScriptAsync($"updateMarker({pt.lat}, {pt.lon}, {label})");
                        });
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"JSON 파싱 오류: {ex.Message} / {line}");
                }
            }

            string err = await p.StandardError.ReadToEndAsync();
            if (!string.IsNullOrWhiteSpace(err))
                Debug.WriteLine("Python stderr:\n" + err);

            return (lastCoord, lastLabel);
        }
        private static (string scriptPath, string workingDir) ResolveGeoPandasScript()
        {
            var script = Path.Combine(AppContext.BaseDirectory, "GeoPandasTest.py");
            var dir = Path.GetDirectoryName(script)!;
            return (script, dir);
        }
        private async void playToolStripMenuItem_Click(object sender, EventArgs e)
        {
            await webView21.CoreWebView2.ExecuteScriptAsync("showLoadingMessage();");

            var item = (ToolStripMenuItem)sender;
            string originalText = item.Text;

            PointDto? lastCoord = null;
            string? lastLabel = null;

            try
            {
                await webView21.ExecuteScriptAsync("initFocus();");

                item.Enabled = false;
                item.Text = "Running...";

                //var workingDir = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, @"..\..\GeoPandas"));
                var (scriptPath, workingDir) = ResolveGeoPandasScript();
                var pythonExe = "python";

                (lastCoord, lastLabel) = await RunPythonAndStreamPointsAsync
                (
                    pythonExe: pythonExe,
                    scriptPath: scriptPath,
                    workingDir: workingDir
                );
            }
            finally
            {
                await webView21.CoreWebView2.ExecuteScriptAsync("hideLoadingMessage();");

                if (lastCoord != null)
                {
                    var focusScript = string.Format(System.Globalization.CultureInfo.InvariantCulture,
                        "focusTo({0}, {1}, {2})", lastCoord.lat, lastCoord.lon, 3);
                    await webView21.ExecuteScriptAsync(focusScript);
                    await webView21.ExecuteScriptAsync($"updateMarker_pop({lastCoord.lat}, {lastCoord.lon}, {lastLabel})");
                }

                item.Enabled = true;
                item.Text = originalText;
            }
        }
    }
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
}
