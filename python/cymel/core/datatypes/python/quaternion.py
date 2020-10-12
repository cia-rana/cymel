# -*- coding: utf-8 -*-
u"""
クォータニオンクラス。
"""
from ...common import *
import maya.api.OpenMaya as _api2
from math import acos, sin

__all__ = ['Quaternion', 'Q']

_MQ = _api2.MQuaternion
_MV = _api2.MVector
_MP = _api2.MPoint
_ME = _api2.MEulerRotation
_MX = _api2.MTransformationMatrix

_2_squadPt = _MQ.squadPt
_TOLERANCE = _MQ.kTolerance


#------------------------------------------------------------------------------
class Quaternion(object):
    u"""
    クォータニオンクラス。

    コンストラクタでは以下の値を指定可能。

    - `Quaternion`
    - x, y, z, w
    - 4値のシーケンス
    - 回転軸 (`.Vector`), 角度
    - 角度, 回転軸 (`.Vector`)
    - `.EulerRotation`
    - `.Matrix`
    """
    __slots__ = ('__data',)
    __hash__ = None

    def __new__(cls, *args):
        n = len(args)
        if n is 1:
            v = args[0]
            #if hasattr(v, '_Quaternion__data'):
            #    return _newQ(_MQ(v.__data), cls)
            if hasattr(v, '_EulerRotation__data'):
                return _newQ(v._EulerRotation__data.asQuaternion(), cls)
            if hasattr(v, '_Matrix__data'):
                return _newQ(_MX(v._Matrix__data).rotation(True), cls)
        elif n >= 2:
            v0 = args[0]
            v1 = args[1]
            if hasattr(v0, '_Vector__data'):
                args = list(args)
                if hasattr(v1, '_Vector__data'):
                    # (Vetor, Vector, [t])
                    args[0] = _MV(v0._Vector__data)
                    args[1] = _MV(v1._Vector__data)
                else:
                    # (Axis, Angle)
                    args[1] = _MV(v0._Vector__data)
                    args[0] = v1
            elif hasattr(v1, '_Vector__data'):
                # (Angle, Axis)
                args = list(args)
                args[1] = _MV(v1._Vector__data)
        try:
            return _newQ(_MQ(*args), cls)
        except:
            raise ValueError(cls.__name__ + ' : not matching constructor found.')

    def __reduce__(self):
        return type(self), tuple(self.__data)

    def __repr__(self):
        return type(self).__name__ + str(self.__data)

    def __str__(self):
        return str(self.__data)

    def __len__(self):
        return 4

    def __getitem__(self, i):
        return self.__data[i]

    def __setitem__(self, i, v):
        self.__data[i] = v

    def __getattr__(self, k):
        try:
            return getattr(self.__data, k)
        except:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, k))

    def __setattr__(self, k, v):
        try:
            return setattr(self.__data, k, v)
        except:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, k))

    def __eq__(self, v):
        try:
            return self.__data == v.__data
        except:
            return False

    def __ne__(self, v):
        try:
            return self.__data != v.__data
        except:
            return True

    def __neg__(self):
        return _newQ(self.__data.__neg__())

    def __add__(self, v):
        try:
            return _newQ(self.__data.__add__(v.__data))
        except:
            raise ValueError("%s + %r" % (type(self).__name__, v))

    def __sub__(self, v):
        try:
            return _newQ(self.__data.__sub__(v.__data))
        except:
            raise ValueError("%s - %r" % (type(self).__name__, v))

    def __mul__(self, v):
        if isinstance(v, Number):
            return _newQ(self.__data.__rmul__(v))  # MQuaternion のスカラー倍は __rmul__ のみ。
        try:
            return _newQ(self.__data.__mul__(v.__data))
        except:
            raise ValueError("%s * %r" % (type(self).__name__, v))

    def __rmul__(self, v):
        try:
            return _newQ(self.__data.__rmul__(v))
        except:
            raise ValueError("%r * %s" % (v, type(self).__name__))

    def __div__(self, v):
        try:
            return _newQ(self.__data.__rmul__(1. / v))
        except:
            raise ValueError("%s / %r" % (type(self).__name__, v))

    def __rdiv__(self, v):
        try:
            d = self.__data
            return _newQ(_MQ(v / d[0], v / d[1], v / d[2], v / d[3]))
        except:
            raise ValueError("%r / %s" % (v, type(self).__name__))

    if MAYA_VERSION < (2015,):
        def isEquivalent(self, q, tol=_TOLERANCE):
            u"""
            ほぼ等価かどうか。符号反転は同じ回転姿勢を表すものとして等価とみなす。

            符号反転を等価とみなしたくない場合は
            `isSignedEquivalent` を利用すると良い。

            :type q: `Quaternion`
            :param q: 比較するクォータニオン。
            :param `float` tol: 許容誤差。
            :rtype: `bool`

            .. note::
                :mayaapi2:`MQuaternion` の isEquivalent では、
                2015 未満では符号反転は等価とみなされなかったが、
                2015 以降で等価とみなされるように変更された。

                cymel では現在の API の仕様に合わせ、
                どのバージョンでも一貫して等価とみなすようにしている。
            """
            try:
                if self.__data[3] * q.__data[3] < 0.:
                    return self.__data.isEquivalent(-q.__data, tol)
                else:
                    return self.__data.isEquivalent(q.__data, tol)
            except:
                return False

        def isSignedEquivalent(self, q, tol=_TOLERANCE):
            u"""
            ほぼ同値かどうか。符号反転は同値とみなさない。

            符号反転も等価とみなしたい場合は
            `isEquivalent` を利用すると良い。

            :type q: `Quaternion`
            :param q: 比較するクォータニオン。
            :param `float` tol: 許容誤差。
            :rtype: `bool`
            """
            try:
                return self.__data.isEquivalent(q.__data, tol)
            except:
                return False

    else:
        def isEquivalent(self, q, tol=_TOLERANCE):
            u"""
            ほぼ等価かどうか。符号反転は同じ回転姿勢を表すものとして等価とみなす。

            符号反転を等価とみなしたくない場合は
            `isSignedEquivalent` を利用すると良い。

            :type q: `Quaternion`
            :param q: 比較するクォータニオン。
            :param `float` tol: 許容誤差。
            :rtype: `bool`

            .. note::
                :mayaapi2:`MQuaternion` の isEquivalent では、
                2015 未満では符号反転は等価とみなされなかったが、
                2015 以降で等価とみなされるように変更された。

                cymel では現在の API の仕様に合わせ、
                どのバージョンでも一貫して等価とみなすようにしている。
            """
            try:
                return self.__data.isEquivalent(q.__data, tol)
            except:
                return False

        def isSignedEquivalent(self, q, tol=_TOLERANCE):
            u"""
            ほぼ同値かどうか。符号反転は同値とみなさない。

            符号反転も等価とみなしたい場合は
            `isEquivalent` を利用すると良い。

            :type q: `Quaternion`
            :param q: 比較するクォータニオン。
            :param `float` tol: 許容誤差。
            :rtype: `bool`
            """
            try:
                return (
                    self.__data.isEquivalent(q.__data, tol) and
                    self.__data[3] * q.__data[3] >= 0.
                )
            except:
                return False

    def set(self, *args):
        u"""
        他の値をセットする。

        コンストラクタと同様に、以下の値を指定可能。

        - `Quaternion`
        - x, y, z, w
        - 4値までのシーケンス
        - 回転軸 (`.Vector`), 角度
        - 角度, 回転軸 (`.Vector`)
        - `.EulerRotation`
        - `.Matrix`

        :rtype: `Quaternion` (self)
        """
        v0 = args[0]
        n = len(args)
        if n is 1:
            if hasattr(v0, '_Quaternion__data'):
                self.__data.setValue(v0.__data)
                return self
            if hasattr(v0, '_EulerRotation__data'):
                self.__data.setValue(v0._EulerRotation__data)
                return self
            if hasattr(v0, '_Matrix__data'):
                _Q_setdata(self, _MX(v0._Matrix__data).rotation(True))
                return self
        elif n is 2:
            if hasattr(v0, '_Vector__data'):
                _Q_setdata(self, _MQ(args[1], _MV(v0)))
                return self
            v1 = args[1]
            if hasattr(v1, '_Vector__data'):
                _Q_setdata(self, _MQ(v0, _MV(v1)))
                return self
        try:
            for i, v in numerate(args):
                self.__data[i] = v
        except:
            raise ValueError(type(self).__name__ + '.set : unsupported arguments.')
        return self

    setValue = set

    def setToXAxis(self, angle):
        u"""
        X軸回りの回転角度をセットする。

        :param `float` angle: 角度。
        :rtype: `Quaternion` (self)
        """
        self.__data.setToXAxis(angle)
        return self

    def setToYAxis(self, angle):
        u"""
        Y軸回りの回転角度をセットする。

        :param `float` angle: 角度。
        :rtype: `Quaternion` (self)
        """
        self.__data.setToYAxis(angle)
        return self

    def setToZAxis(self, angle):
        u"""
        Z軸回りの回転角度をセットする。

        :param `float` angle: 角度。
        :rtype: `Quaternion` (self)
        """
        self.__data.setToZAxis(angle)
        return self

    def asAxisAngle(self):
        u"""
        軸ベクトルと回転角度として得る。

        :rtype: `.Vector`, `float`
        """
        axis, angle = self.__data.asAxisAngle()
        return _newV(_MP(axis)), angle

    asAA = asAxisAngle  #: `asAxisAngle` の別名。

    def asEulerRotation(self, order=XYZ):
        u"""
        オイラー角回転として得る。

        :param `int` order: 得たい回転オーダー。
        :rtype: `.EulerRotation`

        .. note::
            `EulerRotation` の単位は弧度法なので、
            度数法で得たい場合は `asDegrees` を使用すると良い。
        """
        if order is XYZ:
            return _newE(self.__data.asEulerRotation())
        else:
            e = _ME(0., 0., 0., order)
            e.setValue(self.__data)
            return _newE(e)

    asE = asEulerRotation  #: `asEulerRotation` の別名。

    def asDegrees(self, order=XYZ):
        u"""
        オイラー角回転を度数法の `list` として得る。

        :param `int` order: 得たい回転オーダー。
        :rtype: `list`

        .. note::
            単位を弧度法で得たい場合は `asEulerRotation` を使用すると良い。
        """
        if order is XYZ:
            e = self.__data.asEulerRotation()
        else:
            e = _ME(0., 0., 0., order)
            e.setValue(self.__data)
        return [e[0] * TO_DEG, e[1] * TO_DEG, e[2] * TO_DEG]

    asD = asDegrees  #: `asDegrees` の別名。

    def asMatrix(self):
        u"""
        回転行列として得る。

        :rtype: `.Matrix`
        """
        return _newM(self.__data.asMatrix())

    asM = asMatrix  #: `asMatrix` の別名。

    def asTransformation(self):
        u"""
        トランスフォーメーションとして得る。

        :rtype: `.Transformation`
        """
        return _newX(dict(q=_newQ(_MQ(self.__data))))

    asX = asTransformation  #: `asTransformation` の別名。

    def conjugate(self):
        u"""
        共役クォータニオンを得る。

        :rtype: `Quaternion`
        """
        return _newQ(self.__data.conjugate())

    def conjugateIt(self):
        u"""
        共役クォータニオンをセットする。

        :rtype: `Quaternion` (self)
        """
        self.__data.conjugateIt()
        return self

    def inverse(self):
        u"""
        逆クォータニオンを得る。

        :rtype: `Quaternion`
        """
        return _newQ(self.__data.inverse())

    def invertIt(self):
        u"""
        逆クォータニオンをセットする。

        :rtype: `Quaternion` (self)
        """
        self.__data.invertIt()
        return self

    def normal(self):
        u"""
        正規化クォータニオンを得る。

        :rtype: `Quaternion`
        """
        return _newQ(self.__data.normal())

    def normalize(self):
        u"""
        正規化クォータニオンをセットする。

        :rtype: `Quaternion` (self)
        """
        self.__data.normalizeIt()
        return self

    normalizeIt = normalize

    def negateIt(self):
        u"""
        符号反転クォータニオンをセットする。

        :rtype: `Quaternion` (self)
        """
        self.__data.negateIt()
        return self

    def log(self):
        u"""
        対数クォータニオンを得る。

        :rtype: `Quaternion`
        """
        return _newQ(self.__data.log())

    def exp(self):
        u"""
        対数クォータニオンからクォータニオンを得る。。

        :rtype: `Quaternion`
        """
        return _newQ(self.__data.exp())

    def dot(self, q):
        u"""
        クォータニオンの内積を得る。

        :type q: `Quaternion`
        :param q: もう一方のクォータニオン。
        :rtype: `float`
        """
        d = self.__data
        s = q.__data
        return d[0] * s[0] + d[1] * s[1] + d[2] * s[2] + d[3] * s[3]

    @staticmethod
    def slerp(p, q, t, spin=0):
        u"""
        クォータニオンを球面線形補間する。

        :type p: `Quaternion`
        :param p: 始点クォータニオン。
        :type q: `Quaternion`
        :param q: 終点クォータニオン。
        :param `float` t: 0.0～1.0の補間係数。範囲外も指定可。
        :param `int` spin:
            スピン値。
            デフォルトの0は正方向、-1は逆方向、
            さらに+1や-1すると余分に周回する。
        :rtype: `Quaternion`
        """
        p = p.__data
        q = q.__data
        flip = 1.
        xx = p[0] * q[0]
        yy = p[1] * q[1]
        zz = p[2] * q[2]
        ww = p[3] * q[3]
        cosOmega = xx + yy + zz + ww
        if cosOmega < 0.:
            cosOmega = -cosOmega
            flip = -1.

        if 1. - cosOmega < _TOLERANCE:  # 限りなく同じ姿勢を表すもの同士の場合。
            # 符号反転を考慮して線形補間する（微妙な差もあるので、全要素が反転していない場合も有り得る）。
            return (p * t + q * ((1. - t) * flip)).normalizeIt()

        omega = acos(cosOmega) if cosOmega < 1. else 0.
        phi = omega + spin * PI
        sinOmega = sin(omega)
        a = sin(omega - t * phi) / sinOmega
        b = sin(t * phi) / sinOmega * flip
        return _newQ(_MQ(
            p[0] * a + q[0] * b,
            p[1] * a + q[1] * b,
            p[2] * a + q[2] * b,
            p[3] * a + q[3] * b))

    @staticmethod
    def squad(p, a, b, q, t, spin=0):
        u"""
        クォータニオンを球面曲線補間する。

        :type p: `Quaternion`
        :param p: 始点クォータニオン。
        :type a: `Quaternion`
        :param a: 始点側の制御点。
        :type b: `Quaternion`
        :param b: 終点側の制御点。
        :type q: `Quaternion`
        :param q: 終点クォータニオン。
        :param `float` t: 0.0～1.0の補間係数。範囲外も指定可。
        :param `int` spin:
            スピン値。
            デフォルトの0は正方向、-1は逆方向、
            さらに+1や-1すると余分に周回する。
        :rtype: `Quaternion`
        """
        return _slerp(_slerp(p, q, t), _slerp(a, b, t), 2. * (1. - t) * t, spin)

    @staticmethod
    def squadPt(q0, q1, q2):
        u"""
        `squad` 用の制御点を計算する。

        :type q0: `Quaternion`
        :param q0: 1つめのクォータニオン。
        :type q1: `Quaternion`
        :param q1: 2つめのクォータニオン。
        :type q2: `Quaternion`
        :param q2: 3つめのクォータニオン。
        :rtype: `Quaternion`
        """
        return _newQ(_2_squadPt(q0.__data, q1.__data, q2.__data))

Q = Quaternion  #: `Quaternion` の別名。


def _newQ(data, cls=Q):
    obj = _object_new(cls)
    _Q_setdata(obj, data)
    return obj
_object_new = object.__new__

_Q_setdata = Q._Quaternion__data.__set__

Q.Tolerance = _TOLERANCE  #: 同値とみなす許容誤差。
Q.Identity = immutable(Q())  #: 単位クォータニオン。
Q.Zero = immutable(Q(0., 0., 0., 0.))  #: ゼロ。

_slerp = Q.slerp
