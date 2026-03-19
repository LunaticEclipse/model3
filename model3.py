import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pymc as pm
import arviz as az
from scipy.stats import norm
from scipy.stats import gaussian_kde  # for comparison, not used in KCDE

###################
    #DATA#
###################

nasdaq = ["NVDA"]

data = yf.download(nasdaq, start="2025-08-01", end="2026-03-18", group_by='ticker')

open = data.iloc[:,0]
high = data.iloc[:,1] 
low = data.iloc[:,2] 
close = data.iloc[:,3] 

daymove = (close - open)/open
interday = (open- close.shift(1))/open
interday = interday.iloc[1:]
daymove = daymove.iloc[1:]
n = len(open)

#######################
    #KDE FUNCTION#
#######################

def gaussian_kernel(u):
    """Standard Gaussian kernel."""
    return (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * u**2)

def kde_conditional(x_series, y_series, x_new, bandwidths=None, grid=None):
    """
    Kernel Conditional Density Estimation for a time series.

    Parameters:
    x_series : DATA
    y_series : condition 
    x_new : The CURRENT conditioning value (e.g. last interday move).
    bandwidths : tuple (h_x, h_y), optional
        Bandwidths for x and y. If None, they are estimated using Scott's rule.
    grid : array-like, optional
        Points at which to evaluate the density. If None, a grid is created.

    Returns:
    y_grid : ndarray
        The grid points where the density is evaluated.
    f_grid : ndarray
        The estimated conditional density values on the grid.
    """
    x_series = np.asarray(x_series)
    y_series = np.asarray(y_series)
    n = len(x_series)
    if n < 3:
        raise ValueError("Need at least 3 observations to form transitions.")
    
    # Create transition pairs (x_{t-1}, x_t)
    X = y_series[1:]  # conditioning values (lagged)
    Y = x_series[1:]   # response values
    
    # Bandwidth selection (simple rule-of-thumb)
    if bandwidths is None:
        # Scott's rule for 1D: h = sigma * n^(-1/5)
        h_x = np.std(X) * (len(X) ** (-1/5))
        h_y = np.std(Y) * (len(Y) ** (-1/5))
        # Avoid zero bandwidth if data is constant
        h_x = max(h_x, 1e-6)
        h_y = max(h_y, 1e-6)
    else:
        h_x, h_y = bandwidths
    
    def cond_density(y):
        weights = gaussian_kernel((x_new - X) / h_x) / h_x  # K_hx
        weighted_kernels = weights * gaussian_kernel((y - Y) / h_y) / h_y  # K_hx * K_hy
        numerator = np.sum(weighted_kernels)
        denominator = np.sum(weights)
        if denominator == 0:
            return 0.0
        return numerator / denominator
    
    # Create evaluation grid if not provided
    if grid is None:
        # Use range of Y extended by 20%
        y_min, y_max = Y.min(), Y.max()
        span = y_max - y_min
        y_min -= 0.2 * span
        y_max += 0.2 * span
        grid = np.linspace(y_min, y_max, 200)
    
    f_grid = np.array([cond_density(y) for y in grid])
    return grid, f_grid

# Helper: convert density to CDF (assuming uniform grid)
def density_to_cdf(grid, density):
    dx = grid[1] - grid[0]
    cdf = np.cumsum(density) * dx
    # Ensure it ends at 1 (if the density integrates to 1)
    # If the grid doesn't cover the whole support, the last value will be < 1.
    # We keep it as is – it's the cumulative mass within the grid.
    return cdf


###################
    #CONTROL#
###################

# open price
atm = 182.47  

# the observed interday movement
initial_x = (atm-180.35)/atm

#################
    #GRIDS#
#################


# Precompute a fixed grid for consistent x-axis
common_grid = np.linspace(-0.1, 0.1, 1000)
# dx = 0.0001 = 0.01%

# Initial value
y_grid, f_est = kde_conditional(daymove, interday, initial_x, grid=common_grid)

#################
    #PLOTS#
#################

# Create figure and axis
fig, ax = plt.subplots(figsize=(8, 4))
plt.subplots_adjust(bottom=0.25)

line, = ax.plot(common_grid, f_est, 'b-', label='KCDE estimate')
ax.set_xlabel('Day Move')
ax.set_ylabel('Density')
ax.set_title(f'Conditional density given interday move = {(initial_x*100):.4f}%')
ax.legend()
ax.grid(alpha=0.3)
# Set fixed axis limits (optional, but helps stability)
ax.set_xlim(-0.1, 0.1)

# Create a second line for the normal approximation
normal_line, = ax.plot(common_grid, np.zeros_like(common_grid), 'r--', label='Normal approx')
# Compute mean and variance via numerical integration
dx = common_grid[1] - common_grid[0]
# Ensure density integrates to 1 (it should, but we normalize just in case)
integral = np.trapezoid(f_est, common_grid)
if integral > 0:
    norm_f_est = f_est / integral
else:
    norm_f_est = f_est  # fallback, though unlikely
mean = np.trapezoid(common_grid * norm_f_est, common_grid)
variance = np.trapezoid((common_grid - mean)**2 * norm_f_est, common_grid)
std = np.sqrt(variance)

# Generate normal PDF
normal_pdf = norm.pdf(common_grid, mean, std)
normal_line.set_ydata(normal_pdf)

# Optionally update y-axis limit to fit new density
ax.set_ylim(0, max(f_est.max(), normal_pdf.max()) * 1.1)


#################
    #SLIDER#
#################


# Create slider
ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
# Determine slider range from data (e.g., min and max of daymove)
x_min, x_max = -0.1, 0.1
slider = Slider(ax_slider, '$x_n$', x_min, x_max, valinit=initial_x)

def update(val):
    x_new = slider.val
    y_grid, f_est = kde_conditional(daymove, interday, x_new, grid=common_grid)
    line.set_ydata(f_est)
    ax.set_title(f'Conditional density given interday move = {(x_new*100):.4f}%')
    


    # Compute mean and variance via numerical integration
    dx = common_grid[1] - common_grid[0]
    # Ensure density integrates to 1 (it should, but we normalize just in case)
    integral = np.trapezoid(f_est, common_grid)
    if integral > 0:
        norm_f_est = f_est / integral
    else:
        norm_f_est = f_est  # fallback, though unlikely
    mean = np.trapezoid(common_grid * norm_f_est, common_grid)
    variance = np.trapezoid((common_grid - mean)**2 * norm_f_est, common_grid)
    std = np.sqrt(variance)

    # Generate normal PDF
    normal_pdf = norm.pdf(common_grid, mean, std)
    normal_line.set_ydata(normal_pdf)


    # Optionally update y-axis limit to fit new density
    ax.set_ylim(0, max(f_est.max(), normal_pdf.max()) * 1.1)
    fig.canvas.draw_idle()

slider.on_changed(update)



#######################
    #OPTION CHAIN#
#######################

# After you have computed f_est on common_grid, compute the CDF values on that grid
dx = common_grid[1] - common_grid[0]
cdf_grid = np.cumsum(f_est) * dx   # cumulative distribution at each grid point

# Define strikes
strike = np.arange(160, 215, 2.5)         
required_move = (strike - atm) / atm     

# Interpolate to get the CDF at each required_move, with extrapolation handled
prob = np.interp(required_move, common_grid, cdf_grid, left=0, right=1)

# Compute expected call and put payoffs
expected_call = []
expected_put = []
for K in strike:
    # Payoff arrays over grid
    call_payoff = np.maximum(atm * (1 + common_grid) - K, 0)
    put_payoff = np.maximum(K - atm * (1 + common_grid), 0)
    # Integrate
    exp_call = np.sum(call_payoff * f_est) * dx
    exp_put = np.sum(put_payoff * f_est) * dx
    expected_call.append(exp_call)
    expected_put.append(exp_put)

# Print table
print("\n" + "="*80)
#print(f"Conditioning intraday move: {slider.val*100:.4f}%")
#print("-"*80)
print(f"{'Call Price':>12} {'Strike':>8} {'Put Price':>12}")
print("-"*80)
for ec, s, ep in zip(expected_call, strike, expected_put):
    print(f"{ec:12.2f} {s:8.1f} {ep:12.2f}")
print("="*80)



ax.legend()
plt.show()


