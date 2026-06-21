This here is a part of a project I did for my seminar named "Trustworthy AI", which is all about us humans trusting Artificial Intelligence in various tasks, some mundane (like text/media generation) and others critical (like auto-piloted cars and health monitors).

As you probably know, since you are reading this markdown file, detecting distribution shifts is not always sufficient. In many situations, we need to adapt a model trained on a source domain so that it performs better on a target domain.

The objective was to train a model on a labeled source domain, adapt it using target‑domain data, and evaluate whether target‑domain performance improves.

In this particular folder lies the models I used, the datasets and the 3 main trainings.
Basically I trained a source on normal MNIST, tested it on a rotated version of the same dataset, ran it through an adaptation method (CORAL) and re-ran it on the same rotated angle as the first test.

All the results are hardcoded in the plots but the experiment logs are recorded in the outputs folder. 