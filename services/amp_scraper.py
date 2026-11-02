
import math

from playwright.sync_api import sync_playwright


class AMPScraper:

    def __init__(self, amp_server, username, password):
        self.amp_server = amp_server
        self.username = username
        self.password = password

    def scrape(self):

        server_data = []

        with sync_playwright() as playwright:

            browser = playwright.firefox.launch(headless=True)

            try:
                page = browser.new_page()

                page.set_default_timeout(10000)
                page.set_default_navigation_timeout(15000)

                page.goto(self.amp_server)
                page.wait_for_load_state("networkidle")

                # Login to AMP
                page.locator(
                    'input[name="username"]'
                ).fill(self.username)

                page.locator(
                    'input[name="password"]'
                ).fill(self.password)

                page.locator("#loginButton").click()

                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)

                # Find running servers
                running_divs = page.locator(".statusRunning")

                friendly_name = (
                    running_divs
                    .locator(".ServerEntryTop")
                    .locator(".ServerEntryHeader")
                    .locator('[data-bind="text: friendlyname"]')
                )

                servers = friendly_name.all_text_contents()

                # AMP sometimes duplicates server entries
                servers = servers[:math.ceil(len(servers) / 2)]

                # Extract CPU, RAM and player information
                metrics = (
                    running_divs
                    .locator(".ServerEntryInfo")
                    .locator(".ServerEntryMetrics")
                    .locator(".ServerEntryMetric")
                    .locator(".MetricText")
                    .locator("h4")
                )

                metrics_array = metrics.all_text_contents()

                # AMP duplicates metric entries as well
                metrics_array = metrics_array[:len(metrics_array) // 2]

                for i, server_name in enumerate(servers):

                    metric_index = i * 3

                    if metric_index + 2 >= len(metrics_array):
                        break

                    single_server_data = {
                        "name": server_name,
                        "cpu_usage": metrics_array[metric_index],
                        "ram_usage": metrics_array[metric_index + 1],
                        "player_count": metrics_array[metric_index + 2]
                    }

                    server_data.append(single_server_data)

                return server_data

            finally:
                browser.close()
