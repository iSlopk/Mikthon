#!/usr/bin/env bash

cat <<'EOF'
---------------------------------------
Installing Tepthon is in progress..                                                  
---------------------------------------                                                  


                                                  
Copyright (C) 2020-2024 by TepthonArabic@Github, < https://github.com/zxaax >.
This file is part of < https://github.com/zxaax/TepA > project,
and is released under the "GNU v3.0 License Agreement".
Please see < https://github.com/zxaax/TepA/blob/main/LICENSE >
All rights reserved.
EOF

gunicorn app:app --daemon && python -m Tepthon
