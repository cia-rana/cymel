# -*- coding: utf-8 -*-
u"""
:mayanode:`shape` ノードタイプラッパークラス。
"""
from ...common import *
from ..typeregistry import nodetypes, _FIX_SLOTS
from .cyobject import BIT_DAGNODE, BIT_SHAPE

__all__ = ['Shape']

_createNode = cmds.createNode
_rename = cmds.rename

_relatedNodeTypes = nodetypes.relatedNodeTypes

_RE_SHAPE_NAME_sub = re.compile(r'(\d*)$').sub


#------------------------------------------------------------------------------
class Shape(nodetypes.parentBasicNodeClass('shape')):
    u"""
    :mayanode:`shape` ノードタイプラッパークラス。
    """
    if _FIX_SLOTS:
        __slots__ = tuple()

    TYPE_BITS = BIT_DAGNODE | BIT_SHAPE  #: クラスでサポートしているノードの特徴を表す。

    @classmethod
    def createNode(cls, ttype='transform', **kwargs):
        u"""
        クラスに関連付けられたタイプのシェイプノードを生成する。

        このメソッド自体は生成されたノードの名前（文字列）が返されるが、
        固定引数無しでクラスインスタンスを生成する場合に内部的に呼び出される。

        基底メソッドに対して、
        :mayanode:`shape` 向けに
        :mayanode:`transform` ノードの制御が追加されている。

        parent(またはp)オプションが指定された場合は、
        基底メソッドがそのまま呼び出されるが、
        そうでない場合は、ノード名は :mayanode:`transform`
        ノードに付けられ、シェイプ名はそこから自動的に決められる。

        :param `str` ttype:
            parent(またはp)オプションが指定されない場合に
            シェイプの親として同時生成される
            :mayanode:`transform` 系ノードのタイプ名を指定する。
        :param kwargs:
            :mayacmd:`createNode` コマンドのその他のオプションを指定可能。
        :rtype: `str`

        .. note::
            `nodetypes.registerNodeClass <.NodeTypes.registerNodeClass>`
            で登録するカスタムノードクラスでは、
            ``_verifyNode`` メソッドの条件を満たすための処理を追加するために
            オーバーライドすることを推奨する。
        """
        if 'p' in kwargs or 'parent' in kwargs:
            return super(Shape, cls).createNode(**kwargs)

        # 指定された名前、またはクラス名から決まる名前で transform ノードを生成する。
        clsname = cls.__name__
        typs = _relatedNodeTypes(cls)
        if len(typs) > 1:
            raise TypeError('multiple nodetypes related for: ' + clsname)
        name = kwargs.pop('name', None) or kwargs.pop('n', None) or (clsname[0].lower() + clsname[1:] + '#')
        name = _createNode(ttype, n=name)

        # transform ノードの子としてシェイプを生成する。
        # ノード生成フックを考慮して、名前はリネームでつける。
        kwargs['parent'] = name
        name = _RE_SHAPE_NAME_sub(r'Shape\1', name)
        return _rename(_createNode(typs[0], **kwargs), name)

nodetypes.registerNodeClass(Shape, 'shape')

