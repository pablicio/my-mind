from datetime import datetime as dt
from pathlib import Path
import yaml
import click
import logging

from etl.extract.extract import run_extraction
from etl.load.load import run_embedding_generation
from etl.load.evaluate_load import run_embedding_metrics
from etl.load.evaluate_load import run_chunk_metrics
from etl.transform.transform import run_transformation
from inference.inference import run_inference

@click.command(
    help="""
    MyMind CLI v0.0.1

    Main entrypoint for pipeline execution. 
    This CLI centralizes the execution of MyMind pipelines, 
    from ingestion and transformations to embeddings, metrics, 
    and inference.

    Run the MyMind pipelines with various options.

    By default, the full pipeline is executed in the correct order, 
    using the orchestrator configured in your active ZenML stack.

    Examples:

    \b
    # Run the full pipeline with default options
    python run.py

    \b
    # Run only the extraction step
    python run.py --run-extraction-exec

    \b
    # Run only embedding generation
    python run.py --run-embedding-generation-exec

    \b
    # Run inference step only
    python run.py --run-inference-exec

    \b
    # Export pipeline settings
    python run.py --export-settings
"""
)
@click.option(
    "--run-extraction-exec",
    is_flag=True,
    default=False,
    help="Run the extraction step explicitly.",
)
@click.option(
    "--run-embedding-generation-exec",
    is_flag=True,
    default=False,
    help="Run the embedding generation step explicitly.",
)
@click.option(
    "--run-embedding-metrics-exec",
    is_flag=True,
    default=False,
    help="Run the embedding metrics step explicitly.",
)
@click.option(
    "--run-chunk-metrics-exec",
    is_flag=True,
    default=False,
    help="Run the chunk metrics step explicitly.",
)
@click.option(
    "--run-transformation-exec",
    is_flag=True,
    default=False,
    help="Run the transformation step explicitly.",
)
@click.option(
    "--run-inference-exec",
    is_flag=True,
    default=False,
    help="Run the inference step explicitly.",
)
@click.option(
    "--export-settings",
    is_flag=True,
    default=False,
    help="Export pipeline settings to file.",
)

def main(
    run_extraction_exec: bool = False,
    run_embedding_generation_exec: bool = False,    
    run_embedding_metrics_exec: bool = False,
    run_chunk_metrics_exec: bool = False,
    run_transformation_exec: bool = False,
    run_inference_exec: bool = False,
    export_settings: bool = False,      
) -> None:
    assert (
        run_extraction_exec
        or run_embedding_generation_exec
        or run_embedding_metrics_exec
        or run_chunk_metrics_exec
        or run_transformation_exec
        or run_inference_exec
        or export_settings
    ), "Please specify an action to run."

    if export_settings:
        logging.info("Exporting settings to secrets.")

    root_dir = Path(__file__).resolve().parent
    pipeline_config_path = root_dir / "configs" / "pipeline_paths.yml"

    assert pipeline_config_path.exists(), f"Config file not found: {pipeline_config_path}"

    with open(pipeline_config_path, "r", encoding="utf-8") as f:
        pipeline_config = yaml.safe_load(f)

    # Extrair variáveis
    paths = pipeline_config.get("paths", [])
    raw_dir = pipeline_config.get("raw_dir")
    clean_dir = pipeline_config.get("clean_dir")
    chunks_path = pipeline_config.get("chunks_path")
    embeddings_dir = pipeline_config.get("embeddings_dir")

    # --- Run steps usando pipeline_paths.yml ---
    if run_extraction_exec:
        run_extraction(paths=paths)

    if run_transformation_exec:
        run_transformation(raw_dir, clean_dir, chunks_path)

    if run_embedding_generation_exec:
        run_embedding_generation(chunks_path, embeddings_dir)

    if run_chunk_metrics_exec:
        run_chunk_metrics(chunks_path, embeddings_dir, k=5, sample_size=500)

    if run_embedding_metrics_exec:
        run_embedding_metrics(label_key="source_file", limit=100)

    if run_inference_exec:
        run_inference(mode="cli")

if __name__ == "__main__":
    main()
