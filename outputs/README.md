# Output Metrics

Description of each data file.

## Description



output.4.12.0-custom.csv
    Benchmark on the custom kernel.
    The code might be wrong 
        - The test number for context switch needs update.
        - `thr create Child average:,18916402.496013620,` is an anomaly.
    But overall there is no error.
        - Except the `fork()` one -- the code has no intention to actually limit the number of forked procs.
    

output.4.15.0-101-generic.csv
    Benchmark of Ubuntu 16.04