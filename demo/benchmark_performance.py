#!/usr/bin/env python3
"""
VibeVoice Performance Benchmark Script
Compare generation speed with different optimization settings.
"""

import time
import torch
import os
import tempfile
from pathlib import Path

# Import VibeVoice components
from gradio_demo import VibeVoiceDemo

def benchmark_test(demo_instance, test_script, cfg_scale=1.0, test_name="Test"):
    """Run a benchmark test with given parameters."""
    print(f"\n🧪 Running {test_name}...")
    print(f"   CFG Scale: {cfg_scale}")
    print(f"   Inference Steps: {demo_instance.inference_steps}")
    
    start_time = time.time()
    
    # Use a simple 2-speaker test
    speakers = list(demo_instance.available_voices.keys())[:2]
    
    try:
        # Run generation (non-streaming for benchmark)
        result = list(demo_instance.generate_podcast_streaming(
            num_speakers=2,
            script=test_script,
            speaker_1=speakers[0],
            speaker_2=speakers[1],
            cfg_scale=cfg_scale
        ))
        
        generation_time = time.time() - start_time
        
        # Calculate audio duration from final result
        if result and result[-1][1] is not None:  # Check if we have complete audio
            audio_data = result[-1][1]  # Get complete audio
            if audio_data is not None:
                sample_rate, audio_array = audio_data
                audio_duration = len(audio_array) / sample_rate
                speed_ratio = generation_time / audio_duration
                
                print(f"   ✅ Generation time: {generation_time:.1f}s")
                print(f"   🎵 Audio duration: {audio_duration:.1f}s")
                print(f"   ⚡ Speed ratio: {speed_ratio:.1f}x real-time")
                
                return {
                    'test_name': test_name,
                    'generation_time': generation_time,
                    'audio_duration': audio_duration,
                    'speed_ratio': speed_ratio,
                    'cfg_scale': cfg_scale,
                    'inference_steps': demo_instance.inference_steps
                }
        
        print(f"   ⚠️  Generation completed but no audio output detected")
        return None
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    """Run comprehensive performance benchmarks."""
    
    print("🚀 VibeVoice Performance Benchmark")
    print("=" * 50)
    
    # Short test script for benchmarking
    test_script = """Speaker 0: Welcome to our test podcast!
Speaker 1: Thanks for having me. This is a performance test.
Speaker 0: Let's see how fast we can generate this audio.
Speaker 1: The optimizations should make this much faster.
Speaker 0: Indeed, we're expecting significant improvements.
Speaker 1: That's exciting! Let's wrap up this test."""
    
    # Test different configurations
    test_configs = [
        {'inference_steps': 6, 'cfg_scale': 1.0, 'name': 'Optimized (Current)'},
        {'inference_steps': 8, 'cfg_scale': 1.0, 'name': 'Balanced'},
        {'inference_steps': 6, 'cfg_scale': 1.2, 'name': 'Optimized + Higher CFG'},
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n📊 Testing Configuration: {config['name']}")
        
        # Create demo instance with specific settings
        try:
            demo = VibeVoiceDemo(
                model_path="microsoft/VibeVoice-1.5B",
                device="cuda" if torch.cuda.is_available() else "cpu",
                inference_steps=config['inference_steps']
            )
            
            result = benchmark_test(
                demo, 
                test_script, 
                cfg_scale=config['cfg_scale'],
                test_name=config['name']
            )
            
            if result:
                results.append(result)
                
        except Exception as e:
            print(f"❌ Failed to initialize demo: {e}")
            continue
    
    # Print summary
    if results:
        print("\n📈 BENCHMARK SUMMARY")
        print("=" * 50)
        print(f"{'Configuration':<20} {'Gen Time':<10} {'Audio':<8} {'Speed Ratio':<12}")
        print("-" * 50)
        
        for result in results:
            print(f"{result['test_name']:<20} {result['generation_time']:<10.1f} "
                  f"{result['audio_duration']:<8.1f} {result['speed_ratio']:<12.1f}x")
        
        # Find best performance
        fastest = min(results, key=lambda x: x['speed_ratio'])
        print(f"\n🏆 Fastest Configuration: {fastest['test_name']}")
        print(f"   Speed: {fastest['speed_ratio']:.1f}x real-time")
        print(f"   Settings: {fastest['inference_steps']} steps, CFG {fastest['cfg_scale']}")
        
        # Calculate improvement
        if len(results) > 1:
            baseline = max(results, key=lambda x: x['speed_ratio'])  # Slowest as baseline
            improvement = ((baseline['speed_ratio'] - fastest['speed_ratio']) / baseline['speed_ratio']) * 100
            print(f"   Improvement: {improvement:.1f}% faster than slowest config")
    
    else:
        print("\n❌ No benchmark results available")
    
    print(f"\n✅ Benchmark completed!")

if __name__ == "__main__":
    main()