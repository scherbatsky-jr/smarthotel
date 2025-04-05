import threading
from django.core.management.base import BaseCommand
from agents.iaq_agent import start_iaq_agents
from agents.lifebeing_agent import start_lifebeing_agents
from agents.datalogger_agent import start_datalogger

class Command(BaseCommand):
    help = 'Run all agents in parallel threads'

    def handle(self, *args, **kwargs):
        threads = []

        t1 = threading.Thread(target=start_iaq_agents, daemon=True)
        t2 = threading.Thread(target=start_lifebeing_agents, daemon=True)
        t3 = threading.Thread(target=start_datalogger, daemon=True)

        threads.extend([t1, t2, t3])

        for t in threads:
            t.start()

        self.stdout.write(self.style.SUCCESS("Agents are now running..."))

        # Keep main thread alive
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Shutting down agents..."))
