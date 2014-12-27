import re

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

key_value_regexp = "[\\+]{0,1}[\\w|.|-]+"
hash_regexp = "(#" + key_value_regexp + ")"
src_key_regexp = '([#]{0,1}' + key_value_regexp + ")"


value_regexp = "([a-z|A-Z|0-9|,|.|:|;|_|\-]+|\"[a-z|A-Z|0-9|,|_|.|\-|:|;| ]+\")"

add_log_regexp = hash_regexp + "((:)" + value_regexp + ")?"
add_log_matcher = re.compile(add_log_regexp)
group_notification_regexp = '@(\\w+)'
group_notification_matcher = re.compile(group_notification_regexp)