from __future__ import annotations

import io

import pytest

from pre_commit_hooks.terraform_fmt_tabifypp import main


@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
        (
            b'resource "r" "abc" {\n  cors_rule {\n    string_in_brackets  = ["Authorization"]\n    string_in_brackets2 = ("GET")\n  }\n}\n',
            b'resource "r" "abc" {\n\tcors_rule {\n\t\tstring_in_brackets  = ["Authorization"]\n\t\tstring_in_brackets2 = ("GET")\n\t}\n}\n',
        ),
        (
            b'locals {\n  strings_in_brackets = ["abc", "def", "ghi"]\n}\n',
            b'locals {\n\tstrings_in_brackets = ["abc", "def", "ghi"]\n}\n',
        ),
        (
            b'locals {\n  empty_array = [ ]\n}\n',
            b'locals {\n\tempty_array = []\n}\n',
        ),
        (
            b'resource "r" "iam" {\n  interpolation_in_str = "s3__${aws_s3_bucket.files.id}"\n}\n',
            b'resource "r" "iam" {\n\tinterpolation_in_str = "s3__${ aws_s3_bucket.files.id }"\n}\n',
        ),
        (
            b'resource "r" "iam" {\n  interpolation_in_str = "${struct_key[0]}_${struct_key[1]}"\n}\n',
            b'resource "r" "iam" {\n\tinterpolation_in_str = "${ struct_key[0] }_${ struct_key[1] }"\n}\n',
        ),
        (
            b'locals {\n  skips_escapes_in_strings = "$${var} \\"${local.amount}"\n}\n',
            b'locals {\n\tskips_escapes_in_strings = "$${var} \\"${ local.amount }"\n}\n',
        ),
        (
            b'variable "brackets" {\n  type = map(object({\n    groups   = list(string)\n    policies = list(string)\n  }))\n\n  default = {}\n}\n',
            b'variable "brackets" {\n\ttype = map(object({\n\t\tgroups   = list( string )\n\t\tpolicies = list( string )\n\t}))\n\n\tdefault = {}\n}\n',
        ),
        (
            b'resource "r" "s3" {\n  user = "b"\n  name = "interpolate_in_heredoc"\n\n  policy = <<-EOT\n\t{\n\t\t"Version": "2012-10-17",\n\t\t"Statement": [\n\t\t\t{\n\t\t\t\t"Effect": "Allow",\n\t\t\t\t"Action": [\n\t\t\t\t\t"s3:PutObject"\n\t\t\t\t],\n\t\t\t\t"Resource": [\n\t\t\t\t\t"${ aws_s3_bucket.public-files.arn }/*"\n\t\t\t\t]\n\t\t\t}\n\t\t]\n\t}\n\tEOT\n}\n',
            b'resource "r" "s3" {\n\tuser = "b"\n\tname = "interpolate_in_heredoc"\n\n\tpolicy = <<-EOT\n\t{\n\t\t"Version": "2012-10-17",\n\t\t"Statement": [\n\t\t\t{\n\t\t\t\t"Effect": "Allow",\n\t\t\t\t"Action": [\n\t\t\t\t\t"s3:PutObject"\n\t\t\t\t],\n\t\t\t\t"Resource": [\n\t\t\t\t\t"${ aws_s3_bucket.public-files.arn }/*"\n\t\t\t\t]\n\t\t\t}\n\t\t]\n\t}\n\tEOT\n}\n',
        ),
    )
)
def test_opinionated_spacing(input_s, expected, tmpdir):
    path = tmpdir.join('source.tf')
    path.write_binary(input_s)

    assert main([str(path)]) == 1
    assert path.read_binary() == expected
