from benchopt import BaseSolver, safe_import_context

# Protect the import with `safe_import_context()`. This allows:
# - skipping import to speed up autocompletion in CLI.
# - getting requirements info when all dependencies are not installed.
with safe_import_context() as import_ctx:
    import numpy as np
    import coffeine
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import RidgeCV
    from benchopt.stopping_criterion import SingleRunCriterion
    from benchmark_utils import IdentityTransformer


# The benchmark solvers must be named `Solver` and
# inherit from `BaseSolver` for `benchopt` to work properly.
class Solver(BaseSolver):

    # Name to select the solver in the CLI and to display the results.
    name = 'diag'
    parameters = {'frequency_bands': ['low', 'low-alpha']
                  #   ['low', 'delta', 'theta', 'alpha',
                  #    'beta_low', 'beta_mid',
                  #    'beta_high', 'alpha-theta',
                  #    'low-delta-theta-alpha-beta_low-beta_mid-beta_high']
                  }

    stopping_criterion = SingleRunCriterion()

    def set_objective(self, X, y, n_channels):
        # Pipeline parameters
        self.X, self.y = X, y
        frequency_bands = self.frequency_bands.split('-')
        filter_bank_transformer = coffeine.make_filter_bank_transformer(
            names=frequency_bands,
            method='diag',
        )
        self.model = make_pipeline(
            IdentityTransformer(frequency_bands),
            filter_bank_transformer,
            StandardScaler(),
            RidgeCV(alphas=np.logspace(-5, 10, 100))
        )

    def run(self, n_iter):
        # This is the function that is called to evaluate the solver.
        # It runs the algorithm for a given a number of iterations `n_iter`.
        self.model.fit(self.X, self.y)

    def get_result(self):
        # Return the result from one optimization run.
        # The outputs of this function are the arguments of `Objective.compute`
        # This defines the benchmark's API for solvers' results.
        # it is customizable for each benchmark.
        return self.model
