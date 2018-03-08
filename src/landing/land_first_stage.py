import math
import time
import krpc

def dot_product(u, v):
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

def magnitude(v):
    return math.sqrt(dot_product(v, v))

landing_legs_altitude = 15000
suicide_burn_ending_altitude = 100
suicide_burn_speed_target = 20
soft_landing_speed = 6.0

conn = krpc.connect(name='Falcon 7')
vessel = conn.space_center.active_vessel

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
surf_altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
#velocity = conn.add_stream(getattr, vessel.velocity(vessel.surface_reference_frame))
# speed = conn.add_stream(getattr, vessel.flight(), 'speed')

#get kerbin's body class
bodies = conn.space_center.bodies
kerbin_body = bodies['Kerbin']

# turn on air-brakes
vessel.control.brakes = True
# retract landing gear for re-entry
vessel.control.gear = False

# calculate TWRmax for suicide burn
TWRmax = vessel.available_thrust / (vessel.mass * 9.81)
print('Max thrust to weight ratio: {0}'.format(TWRmax))
velocity = vessel.velocity(kerbin_body.reference_frame)
speed = magnitude(velocity)
print('Vessel speed: {0}'.format(speed))
stopping_distance = (speed ** 2) / ((2.0 * 9.81) * (TWRmax - 1.0))
print('Current stopping distance at {0} meters: {1} meters'.format(speed,stopping_distance))

while True:
    # wait until we are moving slow enough to deploy landing legs
    if altitude() < landing_legs_altitude:
        vessel.control.gear = True
        break

print('Landing gear deployed.')

velocity = vessel.velocity(kerbin_body.reference_frame)
speed = magnitude(velocity)
stopping_distance = (speed ** 2) / ((2.0 * 9.81) * (TWRmax - 1.0))
print('Current stopping distance at {0} meters: {1} meters'.format(speed,stopping_distance))
while True:
    velocity = vessel.velocity(kerbin_body.reference_frame)
    speed = magnitude(velocity)
    stopping_distance = (speed**2)/((2.0*9.81)*(TWRmax - 1.0))
    if surf_altitude() < (stopping_distance + suicide_burn_ending_altitude):
        break

vessel.control.throttle = 1.0
vessel.control.rcs = True
vessel.control.sas = True

while True:
    velocity = vessel.velocity(kerbin_body.reference_frame)
    speed = magnitude(velocity)
    if speed < suicide_burn_speed_target:
        vessel.control.throttle = 0.0
        break

# soft landing:
# part one: slow to target velocity
TWRmax = vessel.available_thrust / (vessel.mass * 9.81)
target_twr = 1.2
vessel.control.throttle = (target_twr / TWRmax)
while True:
    velocity = vessel.velocity(kerbin_body.reference_frame)
    speed = magnitude(velocity)
    if speed < soft_landing_speed:
        break

#part two: target velocity until touchdown
TWRmax = vessel.available_thrust / (vessel.mass * 9.81)
target_twr = 1.0
vessel.control.throttle = (target_twr / TWRmax)
time.sleep(2)
vessel.control.throttle = 0.0
