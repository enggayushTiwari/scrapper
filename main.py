import subprocess
import sys

def main():
    print("=======================================")
    print("  LOCAL LEAD GENERATION PIPELINE")
    print("=======================================\n")
    
    # Phase 1: Scraping Google Maps
    print(">>> Starting Phase 1: Google Maps Scraper (scraper.py) <<<")
    try:
        subprocess.run([sys.executable, 'scripts/scraper.py'], check=True)
        print(">>> Phase 1 Completed Successfully <<<\n")
    except subprocess.CalledProcessError as e:
        print(f"!!! Error running scraper.py: {e} !!!")
        sys.exit(1)
    except FileNotFoundError:
        print("!!! Could not find 'scripts/scraper.py'. !!!")
        sys.exit(1)
        
    # Phase 2, 3 & 4: Enrichment Engine
    print(">>> Starting Phase 2, 3 & 4: Enrichment Engine (enrichment_engine.py) <<<")
    try:
        subprocess.run([sys.executable, 'scripts/enrichment_engine.py'], check=True)
        print(">>> Phase 2, 3 & 4 Completed Successfully <<<\n")
    except subprocess.CalledProcessError as e:
        print(f"!!! Error running enrichment_engine.py: {e} !!!")
        sys.exit(1)
    except FileNotFoundError:
        print("!!! Could not find 'scripts/enrichment_engine.py'. !!!")
        sys.exit(1)
        
    print("=======================================")
    print("  PIPELINE FINISHED")
    print("=======================================")

if __name__ == "__main__":
    main()
