# pdf-summarizer

This is a simple command line program that uses the Gemini API to produce short summaries of PDF files (i.e., papers or presentations) in markdown format.  Example usage:

```
(.venv) carns-x1-11g ~/w/s/p/pdf-summarizer (main =)> ./pdf-summarizer.py test.pdf
Reading contents of test.pdf...
Getting API key...
Using gemini-2.5-flash to generate summary...
(.venv) carns-x1-11g ~/w/s/p/pdf-summarizer (main =)> cat test.pdf.md
## Towards Empirical Roofline Modeling of Distributed Data Services: Mapping the Boundaries of RPC Throughput

### Authors
Philip Carns, Matthieu Dorier, Rob Latham, Shane Snyder, Amal Gueroudji, Seth Ockerman, Jerome Soumagne, Dong Dai, Robert Ross

### Synopsis
This paper introduces an empirical roofline modeling methodology tailored for distributed data services (DDS) on high-performance
computing (HPC) systems, specifically focusing on network-centric metrics like Remote Procedure Call (RPC) rate and network
throughput. The authors adapt the traditional computational roofline model by using a 'service ratio' (servers/clients) as the
independent variable and sustained performance rates as the dependent variable. Key challenges addressed include maximizing
performance on modern HPC platforms through network interface card (NIC) selection policies (e.g., Mochi-plumber) and adaptive
polling strategies (Margo spindown). The methodology involves empirically collecting peak client and server performance parameters
using the Mochi data service framework and its Quintain microservice. The approach is evaluated across four leadership-class HPC
systems (Aurora, Polaris, Frontier, Perlmutter), demonstrating its utility for assessing DDS performance, identifying bottlenecks,
and optimizing deployment configurations. Findings indicate that RPC rate is primarily CPU-bound, while network bandwidth is
limited by available network links and fabric topology, and that the model is particularly accurate when servers are oversubscribed.
```

See `--help` for parameters to control the output format.  It can optionally attempt to find a reference for the paper using Crossref.
