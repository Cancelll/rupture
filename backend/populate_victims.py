from django import setup
import os
import sys
import yaml
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
setup()

from breach.models import Target, Victim


def select_victim(victims):
    print '[*] Victims:'
    for i, v in enumerate(victims):
        print '\tID: {}  -  {} ({} {})'.format(i, v[0], v[1]['target'], v[1]['sourceip'])

    if i != 0:
        try:
            vic_ids = input('[*] Choose victim IDs separated by commas or leave empty to select all: ')
            if isinstance(vic_ids, int):
                vic_ids = (vic_ids, )
        except (SyntaxError, NameError), err:
            if isinstance(err, SyntaxError):
                return [vic[1] for vic in victims]
            elif isinstance(err, NameError):
                print '[!] Invalid victim id.'
                exit(1)
    else:
        vic_ids = (0, )

    assert(isinstance(vic_ids, tuple))

    try:
        victim_list = []
        for vid in vic_ids:
            victim_list.append(victims[int(vid)][1])
    except KeyError:
        print '[!] Invalid victim id.'
        exit(1)
    return victim_list


def create_victim(victim, client_dir):
    try:
        target = Target.objects.filter(name=victim['target'])[0]
    except IndexError:
        print '[!] Invalid target for victim ({}, {}).'.format(victim['target'], victim['sourceip'])
        return

    victim_args = {
        'target': target,
        'snifferendpoint': victim['snifferendpoint'],
        'sourceip': victim['sourceip'],
        'realtimeurl': victim['realtimeurl'],
        'recordscardinality': target.recordscardinality,
        'interface': victim['interface']
    }
    if 'calibration_wait' in victim:
        victim_args['calibration_wait'] = victim['calibration_wait']

    v = Victim(**victim_args)
    v.save()

    print '''Created Victim:
             \tvictim_id: {}
             \ttarget: {}
             \tsnifferendpoint: {}
             \tsourceip: {}
             \tinterface: {}
             \trealtimeurl: {}'''.format(
        v.id,
        v.target.name,
        v.snifferendpoint,
        v.sourceip,
        v.interface,
        v.realtimeurl
    )

    create_client(v.realtimeurl, v.id, client_dir)
    create_injection(v.sourceip, v.id, client_dir)


def create_client(realtimeurl, victimid, client_dir):
    print '[*] Creating client for chosen victim...'
    print '[*] Using the client directory:', client_dir

    with open(os.devnull, 'w') as FNULL:
        p = subprocess.Popen(
            [os.path.join(client_dir, 'build.sh'), str(realtimeurl), str(victimid)],
            cwd=client_dir,
            stdout=FNULL,
            stderr=subprocess.PIPE
        )
        if not p.wait():
            print '[*] Client created in following directory:\n\t{}'.format(os.path.join(client_dir, 'client_{}'.format(victimid)))
        else:
            print '[!] Something went wrong when creating client {}'.format(victimid)


def create_injection(sourceip, victimid, client_dir):
    print '[*] Creating injection script for chosen victim...'

    with open(os.path.join(client_dir, 'inject.sh'), 'r') as f:
        injection = f.read()

    injection = injection.replace('$1', str(sourceip))

    with open(os.path.join(client_dir, 'client_{}/inject.sh'.format(victimid)), 'w') as f:
        f.write(injection)

    print '[*] Injection script created in following directory:\n\t{}'.format(
        os.path.join(
            client_dir, 'client_{}/inject.sh'.format(victimid)
        )
    )


def get_victims(victim_cfg):
    try:
        with open(victim_cfg, 'r') as ymlconf:
            cfg = yaml.load(ymlconf)
    except IOError, err:
        print 'IOError: %s' % err
        exit(1)
    return list(cfg.items())


if __name__ == '__main__':
    victim_cfg = sys.argv[1]
    client_dir = sys.argv[2]
    victims = get_victims(victim_cfg)
    try:
        victim_list = select_victim(victims)
        for victim in victim_list:
            try:
                create_victim(victim, client_dir)
            except ValueError:
                print '[!] Invalid parameters for victim ({}, {}).'.format(victim['target'], victim['sourceip'])
    except KeyboardInterrupt:
        print ''
        exit(1)
