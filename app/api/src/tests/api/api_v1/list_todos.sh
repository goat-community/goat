for filename in *.py; do
    if grep -q '# TODO:' $filename;
    then
        echo "### $filename"
        sed -n -e '/^# TODO:/p' $filename| sed -e "s/^# TODO://" | sed 's/.*/- [ ]&/'
    fi
done