from __future__ import print_function

import io
import json
import math
import os
import random
import re


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOURCE_RUN = os.path.join(ROOT, "04_solve", "R201_N08_S0101_COUNT")
SOURCE_JOB = "V07_D30_AFB_N08_S0101_EPS10_C3D8_TAU050_PLOW"
SOURCE_INP = os.path.join(SOURCE_RUN, SOURCE_JOB + ".inp")
SOURCE_FOR = os.path.join(HERE, "pressure_feedback_axial.for")

RADIUS = 4.9
LENGTH = 5.0
HALF_LENGTH = 0.5 * LENGTH
VESSEL_RADIUS = 15.0
CLEARANCE = 0.02
BOTTOM_GAP_MIN = 0.02
BOTTOM_GAP_MAX = 0.05
NONPARALLEL_INITIAL_DEG = 25.0
STRONGLY_TILTED_INITIAL_DEG = 30.0

CASES = (
    ("R224_N08_RANDOM_LOW_E", "V07_D30_AFB_N08_RLOW_E_EPS10_C3D8_TAU050", 22401, 20.0),
    ("R225_N08_RANDOM_LOW_F", "V07_D30_AFB_N08_RLOW_F_EPS10_C3D8_TAU050", 22501, 20.0),
)


try:
    text_type = unicode
except NameError:
    text_type = str


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as stream:
        return stream.read()


def write_text(path, value):
    folder = os.path.dirname(path)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    if not isinstance(value, text_type):
        value = value.decode("utf-8")
    with io.open(path, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(value)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scale(a, value):
    return tuple(value * x for x in a)


def norm(a):
    return math.sqrt(dot(a, a))


def clamp(value, low, high):
    return max(low, min(high, value))


def random_axis(rng):
    # Random azimuth with a deliberately broad, nonvertical tilt distribution.
    tilt = math.radians(rng.uniform(25.0, 85.0))
    if rng.random() < 0.5:
        tilt = math.pi - tilt
    azimuth = rng.uniform(0.0, 2.0 * math.pi)
    return (
        math.sin(tilt) * math.cos(azimuth),
        math.sin(tilt) * math.sin(azimuth),
        math.cos(tilt),
    )


def support_z(axis):
    horizontal = math.sqrt(axis[0] ** 2 + axis[1] ** 2)
    return HALF_LENGTH * abs(axis[2]) + RADIUS * horizontal


def support_radial(axis):
    horizontal = math.sqrt(axis[0] ** 2 + axis[1] ** 2)
    return RADIUS + HALF_LENGTH * horizontal


def segment_endpoints(placement):
    center = placement["center"]
    axis = placement["axis"]
    return add(center, scale(axis, -HALF_LENGTH)), add(center, scale(axis, HALF_LENGTH))


def segment_distance(p1, q1, p2, q2):
    # Closest distance between two finite 3-D line segments (Ericson form).
    d1 = sub(q1, p1)
    d2 = sub(q2, p2)
    r = sub(p1, p2)
    a = dot(d1, d1)
    e = dot(d2, d2)
    f = dot(d2, r)
    eps = 1.0e-14
    if a <= eps and e <= eps:
        return norm(sub(p1, p2))
    if a <= eps:
        s = 0.0
        t = clamp(f / e, 0.0, 1.0)
    else:
        c = dot(d1, r)
        if e <= eps:
            t = 0.0
            s = clamp(-c / a, 0.0, 1.0)
        else:
            b = dot(d1, d2)
            denominator = a * e - b * b
            s = clamp((b * f - c * e) / denominator, 0.0, 1.0) if denominator > eps else 0.0
            t = (b * s + f) / e
            if t < 0.0:
                t = 0.0
                s = clamp(-c / a, 0.0, 1.0)
            elif t > 1.0:
                t = 1.0
                s = clamp((b - c) / a, 0.0, 1.0)
    closest1 = add(p1, scale(d1, s))
    closest2 = add(p2, scale(d2, t))
    return norm(sub(closest1, closest2))


def pair_clearance(a, b):
    return segment_distance(*(segment_endpoints(a) + segment_endpoints(b))) - 2.0 * RADIUS


def horizontal_support(axis, direction):
    projection = dot(axis, direction)
    return HALF_LENGTH * abs(projection) + RADIUS * math.sqrt(max(0.0, 1.0 - projection * projection))


def horizontal_separation_clearance(a, b):
    delta = (b["center"][0] - a["center"][0], b["center"][1] - a["center"][1], 0.0)
    distance = norm(delta)
    if distance <= 1.0e-12:
        return -1.0e30
    direction = scale(delta, 1.0 / distance)
    return distance - horizontal_support(a["axis"], direction) - horizontal_support(b["axis"], direction)


def geometry_clearance(a, b):
    az0 = a["center"][2] - support_z(a["axis"])
    az1 = a["center"][2] + support_z(a["axis"])
    bz0 = b["center"][2] - support_z(b["axis"])
    bz1 = b["center"][2] + support_z(b["axis"])
    vertical_gap = max(az0 - bz1, bz0 - az1)
    if vertical_gap >= 0.0:
        return vertical_gap
    # A separating plane normal to the horizontal center-to-center direction.
    # Positive clearance proves the two finite cylinders do not intersect.
    return horizontal_separation_clearance(a, b)


def candidate_placement(rng, height_limit):
    axis = random_axis(rng)
    z_support = support_z(axis)
    radial_limit = VESSEL_RADIUS - support_radial(axis) - CLEARANCE
    z_low = z_support + rng.uniform(BOTTOM_GAP_MIN, BOTTOM_GAP_MAX)
    z_high = height_limit - z_support - CLEARANCE
    if radial_limit <= 0.0 or z_high < z_low:
        return None
    radius = radial_limit * math.sqrt(rng.random())
    azimuth = rng.uniform(0.0, 2.0 * math.pi)
    return {
        "center": (radius * math.cos(azimuth), radius * math.sin(azimuth), rng.uniform(z_low, z_high)),
        "axis": axis,
        "spin_deg": rng.uniform(0.0, 360.0),
    }


def make_layout(seed, height_limit):
    rng = random.Random(seed)
    best = None
    # Two low layers (4+4). Layers are separated by their exact vertical
    # support boxes; within each layer a conservative capsule test is used.
    for restart in range(12000):
        placements = []
        layer_bottom = rng.uniform(BOTTOM_GAP_MIN, BOTTOM_GAP_MAX)
        failed = False
        for layer_count in (4, 4):
            layer = None
            for layer_attempt in range(300):
                trial = []
                phase = rng.uniform(0.0, 2.0 * math.pi)
                ring_radius = rng.uniform(7.20, 7.50)
                for index in range(layer_count):
                    theta = phase + 2.0 * math.pi * index / layer_count + math.radians(rng.uniform(-7.0, 7.0))
                    radius = ring_radius + rng.uniform(-0.20, 0.20)
                    tilt = math.radians(rng.uniform(88.0, 89.8))
                    if rng.random() < 0.5:
                        tilt = math.pi - tilt
                    axis_azimuth = theta + 0.5 * math.pi + math.radians(rng.uniform(-22.0, 22.0))
                    axis = (
                        math.sin(tilt) * math.cos(axis_azimuth),
                        math.sin(tilt) * math.sin(axis_azimuth),
                        math.cos(tilt),
                    )
                    candidate = {
                        "center": (radius * math.cos(theta), radius * math.sin(theta), layer_bottom + support_z(axis)),
                        "axis": axis,
                        "spin_deg": rng.uniform(0.0, 360.0),
                    }
                    if math.hypot(candidate["center"][0], candidate["center"][1]) + support_radial(axis) > VESSEL_RADIUS - CLEARANCE + 1.0e-9:
                        break
                    if any(horizontal_separation_clearance(candidate, old) < CLEARANCE - 1.0e-9 for old in trial):
                        break
                    trial.append(candidate)
                if len(trial) == layer_count:
                    layer = trial
                    break
            if layer is None:
                failed = True
                break
            placements.extend(layer)
            layer_top = max(item["center"][2] + support_z(item["axis"]) for item in layer)
            layer_bottom = layer_top + CLEARANCE + rng.uniform(0.0, 0.02)
        if failed or len(placements) != 8:
            continue
        max_z = max(item["center"][2] + support_z(item["axis"]) for item in placements)
        if not 10.0 <= max_z <= 20.0:
            continue
        angles = [math.degrees(math.acos(clamp(abs(item["axis"][2]), 0.0, 1.0))) for item in placements]
        if sum(angle >= NONPARALLEL_INITIAL_DEG for angle in angles) < 5:
            continue
        if sum(angle >= STRONGLY_TILTED_INITIAL_DEG for angle in angles) < 3:
            continue
        min_clearance = min(geometry_clearance(placements[i], placements[j]) for i in range(8) for j in range(i))
        score = (max_z, -min_clearance, restart)
        if best is None or score < best[0]:
            best = (score, placements, angles, min_clearance)
            if max_z <= height_limit - 0.25:
                break
    if best is None:
        raise RuntimeError("no feasible layout for seed={} height={}".format(seed, height_limit))
    return best[1], best[2], best[3]


def rotation_from_z(axis):
    ux, uy, uz = axis
    horizontal = math.sqrt(ux * ux + uy * uy)
    angle = math.degrees(math.acos(clamp(uz, -1.0, 1.0)))
    if horizontal < 1.0e-12:
        return ((1.0, 0.0, 0.0), angle) if uz < 0.0 else None
    return ((-uy / horizontal, ux / horizontal, 0.0), angle)


def instance_transform(placement):
    center = placement["center"]
    axis = placement["axis"]
    origin = add(center, scale(axis, -HALF_LENGTH))
    lines = ["{:.12g}, {:.12g}, {:.12g}".format(*origin)]
    rotation = rotation_from_z(axis)
    if rotation is not None:
        rotation_axis, angle = rotation
        endpoint = add(origin, rotation_axis)
        lines.append("{:.12g}, {:.12g}, {:.12g}, {:.12g}, {:.12g}, {:.12g}, {:.12g}".format(
            origin[0], origin[1], origin[2], endpoint[0], endpoint[1], endpoint[2], angle
        ))
    # Circular sponge geometry makes spin irrelevant to overlap, but a spin value is retained in metadata.
    return "\n".join(lines) + "\n"


def replace_instances(text, placements):
    for index, placement in enumerate(placements, 1):
        pattern = re.compile(
            r"(\*Instance, name=Sponge-{0:02d}, part=Part-1\n).*?(\*End Instance)".format(index),
            re.I | re.S,
        )
        transform = instance_transform(placement)
        text, count = pattern.subn(lambda match: match.group(1) + transform + match.group(2), text, count=1)
        if count != 1:
            raise RuntimeError("could not replace Sponge-{:02d}".format(index))
    return text


def settle_only_text(formal_text, settle_job):
    marker = "*Step, name=SWELL"
    position = formal_text.find(marker)
    if position < 0:
        raise RuntimeError("SWELL step not found")
    result = formal_text[:position]
    result = re.sub(r"\A\*Heading\n(?:\*\*.*\n)*", "*Heading\n** SETTLE-only orientation screen job={}\n".format(settle_job), result, count=1)
    return result


def generate(run_id, job_name, seed, height_limit):
    placements, angles, min_clearance = make_layout(seed, height_limit)
    max_z = max(item["center"][2] + support_z(item["axis"]) for item in placements)
    source = read_text(SOURCE_INP)
    formal = re.sub(
        r"\A\*Heading\n(?:\*\*.*\n)*",
        "*Heading\n** V07 N08 randomized low-height layout {} seed={}\n** Axial feedback job={}\n".format(run_id, seed, job_name),
        source,
        count=1,
    )
    formal = replace_instances(formal, placements)
    run_dir = os.path.join(ROOT, "04_solve", run_id)
    inp_path = os.path.join(run_dir, job_name + ".inp")
    settle_job = job_name + "_SETTLE"
    settle_path = os.path.join(run_dir, settle_job + ".inp")
    write_text(inp_path, formal)
    write_text(settle_path, settle_only_text(formal, settle_job))
    config = {
        "run_id": run_id,
        "job_name": job_name,
        "settle_screen_job_name": settle_job,
        "status": "GENERATED_AWAITING_DATACHECK_AND_SETTLE_SCREEN",
        "workflow": "V07_D30_axial_pressure_feedback",
        "study": "N08_random_low_initial_height",
        "layout_seed": seed,
        "height_limit_mm": height_limit,
        "initial_max_z_mm": max_z,
        "minimum_capsule_clearance_mm": min_clearance,
        "initial_overlap_check": "PASS_conservative_finite_axis_capsules",
        "initial_nonparallel_threshold_deg": NONPARALLEL_INITIAL_DEG,
        "initial_strong_tilt_threshold_deg": STRONGLY_TILTED_INITIAL_DEG,
        "initial_nonparallel_count": sum(angle >= NONPARALLEL_INITIAL_DEG for angle in angles),
        "initial_strong_tilt_count": sum(angle >= STRONGLY_TILTED_INITIAL_DEG for angle in angles),
        "settled_nonparallel_threshold_deg": 15.0,
        "settled_nonparallel_required_count": 3,
        "sponge_count": 8,
        "feedback_measure": "max(-S33_local, 0)",
        "diagnostic_measure": "max(PRESS, 0)",
        "p_on_MPa": 0.00002,
        "p_stop_MPa": 0.00010,
        "tau_s": 0.5,
        "epsilon_free_max": 10.0,
        "element_type": "C3D8",
        "settle_duration_s": 2.0,
        "swell_duration_s": 5.0,
        "input_path": inp_path,
        "settle_screen_input_path": settle_path,
        "user_subroutine": SOURCE_FOR,
        "placements": [
            {
                "instance": "Sponge-{:02d}".format(index),
                "center_mm": list(item["center"]),
                "axis": list(item["axis"]),
                "spin_deg": item["spin_deg"],
                "initial_axis_angle_to_vessel_deg": angles[index - 1],
            }
            for index, item in enumerate(placements, 1)
        ],
    }
    write_text(os.path.join(run_dir, "configuration.json"), json.dumps(config, indent=2, sort_keys=True) + "\n")
    return run_id, seed, max_z, min_clearance, angles


def main():
    for case in CASES:
        run_id, seed, max_z, min_clearance, angles = generate(*case)
        print("{} seed={} max_z={:.6g} min_clearance={:.6g} angles={}".format(
            run_id, seed, max_z, min_clearance, ",".join("{:.1f}".format(value) for value in angles)
        ))


if __name__ == "__main__":
    main()
