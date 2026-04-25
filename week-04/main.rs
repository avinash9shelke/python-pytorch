use std::time::Instant;

const A: u32 = 1664525;
const C: u32 = 1013904223;

#[inline(always)]
fn lcg_next(state: &mut u32) -> u32 {
    *state = state.wrapping_mul(A).wrapping_add(C);
    *state
}

#[inline(always)]
fn max_subarray_sum(n: usize, seed: u32, min_val: i128, max_val: i128) -> i128 {
    let mut state = seed;
    let range = max_val - min_val + 1;
    // Assume valid input where range > 0
    let use_u32 = range <= (u32::MAX as i128);
    let r32 = if use_u32 { range as u32 } else { 0 };
    let r128 = if use_u32 { 0 } else { range as u128 };

    // Kadane's algorithm
    let mut best: i128 = i128::MIN;
    let mut curr: i128 = 0;

    let mut i = 0;
    while i < n {
        let v = lcg_next(&mut state);
        let rem_i128: i128 = if use_u32 {
            (v % r32) as i128
        } else {
            ((v as u128) % r128) as i128
        };
        let x = rem_i128 + min_val;

        if curr > 0 {
            curr += x;
        } else {
            curr = x;
        }
        if curr > best {
            best = curr;
        }

        i += 1;
    }
    best
}

#[inline(always)]
fn total_max_subarray_sum(n: usize, initial_seed: u32, min_val: i128, max_val: i128) -> i128 {
    let mut total: i128 = 0;
    let mut gen_state = initial_seed;
    let mut k = 0;
    while k < 20 {
        let seed = lcg_next(&mut gen_state);
        total += max_subarray_sum(n, seed, min_val, max_val);
        k += 1;
    }
    total
}

fn main() {
    let n: usize = 10000;
    let initial_seed: u32 = 42;
    let min_val: i128 = -10;
    let max_val: i128 = 10;

    let start = Instant::now();
    let result = total_max_subarray_sum(n, initial_seed, min_val, max_val);
    let elapsed = start.elapsed().as_secs_f64();

    println!("Total Maximum Subarray Sum (20 runs): {}", result);
    println!("Execution Time: {:.6} seconds", elapsed);
}