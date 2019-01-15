from subprocess import check_call, check_output, call
fp = open('raw_kern', 'w')
call(['ls', '/boot'], stdout=fp)

versions = []
with open('raw_kern', 'r') as fp:
    lines = fp.readlines()
    for l in lines:
        if 'vmlinuz' in l:
            full_name = l.strip('vmlinuz-').strip()
            #print full_name
            num_name = full_name.strip('-generic')
            if '-' in num_name:
		version_seg = num_name.split('-')
            elif 'c' in num_name:
            	version_seg = num_name.split('c')
            elif 'd' in num_name:
            	version_seg = num_name.split('d')

            first_versions = version_seg[0].split('.')
            #second_version = version_seg[1]
            ident = []
	    print version_seg
            for s in first_versions:
                ident.append(int(s))
            length = len(ident)
            assert length == 3
            #ident.append(int(second_version))
            ident.append(full_name)
            versions.append(ident)
versions = sorted(versions, key = lambda x : (x[0], x[1], x[2]))

with open('kern_list', 'w') as fp:
    for v in versions:
        print v
        fp.write(v[3]+'\n')

