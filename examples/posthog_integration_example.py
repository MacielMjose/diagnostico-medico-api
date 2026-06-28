#!/usr/bin/env python3
"""
Example: PostHog Integration Usage
This script demonstrates how to use PostHog integration for analytics.
"""

from datetime import datetime

from app.core.config import Settings
from app.monitoring.posthog import (
    capture_event,
    capture_llm_request,
    capture_prediction,
    capture_request,
    init_posthog,
)

# Initialize PostHog with settings
settings = Settings()
client = init_posthog(settings)

if not client:
    print("PostHog is not enabled. Set POSTHOG_ENABLED=true and POSTHOG_API_KEY")
    exit(1)

print("PostHog Integration Examples")
print("=" * 50)

# Example 1: Capture a simple event
print("\n1. Capturing a simple event...")
capture_event("user_signup", "user_123", {"plan": "premium"})
print("✓ Event 'user_signup' captured")

# Example 2: Capture an API request
print("\n2. Capturing an API request...")
capture_request(
    endpoint="/api/v1/predict",
    method="POST",
    status_code=200,
    duration=0.245,  # 245ms
)
print("✓ Event 'api_request' captured")

# Example 3: Capture a model prediction
print("\n3. Capturing a model prediction...")
capture_prediction(
    model_name="pcos_model_v1",
    duration=0.150,  # 150ms
    status="success",
)
print("✓ Event 'model_prediction' captured")

# Example 4: Capture an LLM request
print("\n4. Capturing an LLM request...")
capture_llm_request(
    provider="openai",
    model="gpt-4o-mini",
    duration=0.890,  # 890ms
    tokens_used=245,
    status="success",
)
print("✓ Event 'llm_request' captured")

# Example 5: Capture multiple requests in a simulation
print("\n5. Simulating multiple API requests...")
endpoints = [
    "/api/v1/predict",
    "/api/v1/explain",
    "/api/v1/optimize",
    "/health",
]

for endpoint in endpoints:
    # Simulate variable latency
    duration = 0.1 + (hash(endpoint) % 10) * 0.05
    status_code = 200 if hash(endpoint) % 20 != 0 else 500
    capture_request(endpoint, "POST", status_code, duration)
    print(f"  ✓ {endpoint} ({status_code}) - {duration:.3f}s")

# Example 6: Capture batch predictions
print("\n6. Simulating batch predictions...")
models = ["model_v1", "model_v2", "model_v3"]
for model in models:
    duration = 0.05 + (hash(model) % 5) * 0.02
    capture_prediction(model, duration, status="success")
    print(f"  ✓ {model} - {duration:.3f}s")

# Example 7: Capture LLM usage statistics
print("\n7. Simulating LLM usage...")
providers = [
    ("openai", "gpt-4o-mini", 180),
    ("anthropic", "claude-3-haiku", 150),
    ("openai", "gpt-4o-mini", 220),
]

for provider, model, tokens in providers:
    duration = tokens * 0.003  # ~3ms per 100 tokens
    capture_llm_request(provider, model, duration, tokens, "success")
    print(f"  ✓ {provider}/{model} - {tokens} tokens - {duration:.3f}s")

# Example 8: Capture custom business event
print("\n8. Capturing custom business events...")
capture_event(
    "model_optimization_completed",
    properties={
        "original_accuracy": 0.82,
        "optimized_accuracy": 0.90,
        "improvement_percent": 8.8,
        "iterations": 50,
        "timestamp": datetime.now().isoformat(),
    },
)
print("✓ Event 'model_optimization_completed' captured")

# Example 9: Capture error event
print("\n9. Capturing error event...")
capture_request(
    endpoint="/api/v1/predict",
    method="POST",
    status_code=400,
    duration=0.050,
    error="Invalid feature: missing 'Age' field",
)
print("✓ Error event captured")

# Example 10: Using distinct_id for user tracking
print("\n10. Capturing events with distinct_id...")
capture_event(
    "prediction_completed",
    distinct_id="user_doctor_001",
    properties={"patient_id": "p_12345", "confidence": 0.92},
)
print("✓ Event captured with distinct_id 'user_doctor_001'")

print("\n" + "=" * 50)
print("All examples completed!")
print("\nNote: Events are buffered and sent in batches.")
print("Give PostHog a few seconds to process the events.")
print("\nCheck your PostHog dashboard to see the events:")
print("1. Go to Insights")
print("2. Select the event you want to visualize")
print("3. Choose your visualization type (Table, Chart, etc.)")
