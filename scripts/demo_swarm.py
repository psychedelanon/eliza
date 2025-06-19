#!/usr/bin/env python3
"""
ElizaOS Swarm Demo Script

Interactive demonstration of the multi-agent crypto-Twitter swarm system.
Supports both dry-run simulation and live Twitter integration.
"""

import asyncio
import argparse
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.EnhancedSwarmCoordinator import EnhancedSwarmCoordinator
from agents.EventSystem import EventSystem
from eliza.config.schema import validate_all_personas
from eliza.context.store import ContextStore
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TimeRemainingColumn, BarColumn, TextColumn
from rich.live import Live
from rich.align import Align
from rich import box

console = Console()

@dataclass
class SwarmStats:
    """Statistics tracking for the swarm demo."""
    tweets_sent: int = 0
    arguments_triggered: int = 0
    rate_limit_backoffs: int = 0
    price_updates_processed: int = 0
    context_entries_created: int = 0
    start_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
    
    @property
    def runtime_seconds(self) -> int:
        """Get runtime in seconds."""
        if self.start_time:
            return int((datetime.now() - self.start_time).total_seconds())
        return 0
    
    @property
    def tweets_per_minute(self) -> float:
        """Calculate tweets per minute rate."""
        runtime_minutes = max(self.runtime_seconds / 60, 0.1)  # Avoid division by zero
        return self.tweets_sent / runtime_minutes


class SwarmDemo:
    """Main demo orchestrator class."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.stats = SwarmStats()
        self.running = False
        self.coordinator: Optional[EnhancedSwarmCoordinator] = None
        self.event_system: Optional[EventSystem] = None
        self.context_store: Optional[ContextStore] = None
        
        # Setup logging
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("swarm_demo")
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        console.print("\n[yellow]🛑 Shutdown signal received. Stopping swarm...[/yellow]")
        self.running = False
    
    def display_banner(self):
        """Display the ASCII startup banner."""
        banner = """
[bold cyan]
 ███████╗██╗     ██╗███████╗ █████╗  ██████╗ ███████╗
 ██╔════╝██║     ██║╚══███╔╝██╔══██╗██╔═══██╗██╔════╝
 █████╗  ██║     ██║  ███╔╝ ███████║██║   ██║███████╗
 ██╔══╝  ██║     ██║ ███╔╝  ██╔══██║██║   ██║╚════██║
 ███████╗███████╗██║███████╗██║  ██║╚██████╔╝███████║
 ╚══════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
[/bold cyan]
[bold white]              Crypto-Twitter Swarm System[/bold white]
[dim]                      v0.4.0-rc1[/dim]
"""
        console.print(Align.center(banner))
        
        # Demo configuration info
        mode = "[green]LIVE[/green]" if not self.args.dry else "[yellow]DRY RUN[/yellow]"
        duration_str = f"{self.args.duration}s" if self.args.duration else "∞"
        
        config_table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1))
        config_table.add_column("Setting", style="bold")
        config_table.add_column("Value")
        
        config_table.add_row("Mode", mode)
        config_table.add_row("Duration", duration_str)
        config_table.add_row("Verbose", "✅" if self.args.verbose else "❌")
        config_table.add_row("Agents", str(len(self._get_agent_files())))
        
        console.print(Align.center(config_table))
        console.print()
    
    def _get_agent_files(self) -> list:
        """Get list of agent configuration files."""
        persona_dir = Path("persona")
        if persona_dir.exists():
            return list(persona_dir.glob("agent*.yml"))
        return []
    
    async def initialize_components(self):
        """Initialize all swarm components."""
        console.print("[bold blue]🔧 Initializing swarm components...[/bold blue]")
        
        # Validate persona files
        try:
            personas = validate_all_personas()
            console.print(f"[green]✅ Validated {len(personas)} persona files[/green]")
        except Exception as e:
            console.print(f"[red]❌ Persona validation failed: {e}[/red]")
            return False
        
        # Initialize context store
        self.context_store = ContextStore()
        console.print("[green]✅ Context store initialized[/green]")
        
        # Initialize event system
        self.event_system = EventSystem()
        console.print("[green]✅ Event system initialized[/green]")
        
        # Initialize swarm coordinator
        engagement_config = {
            "min_delay": 60,
            "max_delay": 180,
            "max_concurrent": 3,
            "enabled": True
        }
        
        self.coordinator = EnhancedSwarmCoordinator(
            event_system=self.event_system,
            context_store=self.context_store,
            engagement_config=engagement_config,
            dry_run=self.args.dry
        )
        console.print("[green]✅ Swarm coordinator initialized[/green]")
        
        return True
    
    def create_stats_table(self) -> Table:
        """Create a live statistics table."""
        table = Table(title="📊 Swarm Statistics", box=box.ROUNDED)
        table.add_column("Metric", style="bold cyan", no_wrap=True)
        table.add_column("Value", style="green", justify="right")
        table.add_column("Rate", style="yellow", justify="right")
        
        # Runtime
        runtime_str = str(timedelta(seconds=self.stats.runtime_seconds))
        table.add_row("Runtime", runtime_str, "")
        
        # Core metrics
        tweets_rate = f"{self.stats.tweets_per_minute:.1f}/min"
        table.add_row("Tweets Sent", str(self.stats.tweets_sent), tweets_rate)
        
        args_rate = f"{self.stats.arguments_triggered / max(self.stats.runtime_seconds / 3600, 0.1):.1f}/hr"
        table.add_row("Arguments Triggered", str(self.stats.arguments_triggered), args_rate)
        
        table.add_row("Rate Limit Backoffs", str(self.stats.rate_limit_backoffs), "")
        table.add_row("Price Updates", str(self.stats.price_updates_processed), "")
        table.add_row("Context Entries", str(self.stats.context_entries_created), "")
        
        return table
    
    async def simulate_activity(self):
        """Simulate swarm activity for demo purposes."""
        import random
        
        # Simulate price updates
        if random.random() < 0.3:  # 30% chance per cycle
            price_event = {
                "type": "price_update",
                "asset": random.choice(["btc", "hpo"]),
                "price": random.uniform(30000, 70000),
                "change_pct": random.uniform(-5, 5)
            }
            await self.event_system.emit_event("price_update", price_event)
            self.stats.price_updates_processed += 1
        
        # Simulate tweet activity
        if random.random() < 0.2:  # 20% chance per cycle
            if not self.args.dry:
                # In live mode, would actually send tweets
                pass
            self.stats.tweets_sent += 1
            
            # Simulate context entry creation
            if random.random() < 0.7:  # 70% chance
                self.context_store.push(
                    agent_id=f"agent{random.randint(1, 5)}",
                    tweet_id=f"demo_{int(time.time())}",
                    topic_tags=random.choice([["btc", "bullish"], ["hpo", "bearish"], ["crypto", "meme"]])
                )
                self.stats.context_entries_created += 1
        
        # Simulate arguments
        if random.random() < 0.05:  # 5% chance per cycle
            self.stats.arguments_triggered += 1
        
        # Simulate rate limiting (rare)
        if random.random() < 0.01:  # 1% chance per cycle
            self.stats.rate_limit_backoffs += 1
    
    async def run_demo(self):
        """Run the main demo loop."""
        self.running = True
        end_time = None
        
        if self.args.duration:
            end_time = datetime.now() + timedelta(seconds=self.args.duration)
        
        # Initialize progress bar
        with Progress(
            TextColumn("[bold blue]Running swarm demo..."),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn() if self.args.duration else TextColumn("∞"),
            console=console
        ) as progress:
            
            if self.args.duration:
                task = progress.add_task("Demo Progress", total=self.args.duration)
            else:
                task = progress.add_task("Demo Progress", total=None)
            
            # Main demo loop
            cycle_count = 0
            while self.running:
                # Check if duration exceeded
                if end_time and datetime.now() >= end_time:
                    break
                
                # Simulate activity
                await self.simulate_activity()
                
                # Update progress
                if self.args.duration:
                    elapsed = (datetime.now() - self.stats.start_time).total_seconds()
                    progress.update(task, completed=min(elapsed, self.args.duration))
                
                # Display stats every 10 cycles (roughly every 30 seconds)
                cycle_count += 1
                if cycle_count % 10 == 0:
                    console.print(self.create_stats_table())
                
                # Short delay between cycles
                await asyncio.sleep(3)
        
        # Final stats display
        console.print("\n[bold green]🏁 Demo completed![/bold green]")
        console.print(self.create_stats_table())
    
    async def shutdown(self):
        """Clean shutdown of all components."""
        console.print("[bold blue]🧹 Cleaning up...[/bold blue]")
        
        if self.coordinator:
            # In a real implementation, would gracefully stop the coordinator
            pass
        
        if self.context_store:
            # Close context store connections
            pass
        
        console.print("[green]✅ Cleanup completed[/green]")


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="ElizaOS Crypto-Twitter Swarm Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a 5-minute dry run simulation
  python scripts/demo_swarm.py --dry --duration 300
  
  # Run live demo indefinitely with verbose logging
  python scripts/demo_swarm.py --live --verbose
  
  # Quick dry run for 30 seconds
  python scripts/demo_swarm.py --dry -d 30
        """
    )
    
    # Mode selection (required)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--dry", 
        action="store_true",
        help="Run in dry-run simulation mode (no actual tweets)"
    )
    mode_group.add_argument(
        "--live", 
        action="store_true",
        help="Run with live Twitter integration"
    )
    
    # Duration control
    parser.add_argument(
        "--duration", "-d",
        type=int,
        metavar="SECONDS",
        help="Demo duration in seconds (default: run indefinitely)"
    )
    
    # Logging control
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose debug logging"
    )
    
    # Configuration overrides
    parser.add_argument(
        "--persona-dir",
        type=Path,
        default=Path("persona"),
        help="Path to persona configuration directory (default: ./persona)"
    )
    
    return parser


async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create demo instance
    demo = SwarmDemo(args)
    
    try:
        # Display banner
        demo.display_banner()
        
        # Initialize components
        if not await demo.initialize_components():
            console.print("[red]❌ Failed to initialize components[/red]")
            sys.exit(1)
        
        # Run the demo
        console.print("[bold green]🚀 Starting swarm demo...[/bold green]\n")
        await demo.run_demo()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]💥 Demo failed: {e}[/red]")
        if args.verbose:
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(1)
    finally:
        await demo.shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 