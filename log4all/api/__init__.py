__author__ = 'Igor Maculan <n3wtron@gmail.com>'

key_value_regexp = "[\\+]{0,1}[\\w|.|-]+"
hash_regexp = "(#" + key_value_regexp + ")"
src_key_regexp = '([#]{0,1}' + key_value_regexp + ")"
value_regexp = "([a-z|A-Z|0-9|,|.|-]+)"